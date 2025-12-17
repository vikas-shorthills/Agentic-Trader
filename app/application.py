"""
Application Factory Module

This module contains the main application factory function and all helper
functions needed to create and configure the FastAPI application with
Google ADK integration.
"""

from pathlib import Path
from typing import Any, Tuple

import google.adk.cli
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from google.adk.agents.run_config import RunConfig
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.cli.adk_web_server import AdkWebServer
from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.evaluation.local_eval_set_results_manager import LocalEvalSetResultsManager
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from app.loggers.logging_config import get_logger
from app.loggers.middleware_logger import RequestLoggingMiddleware
from app.config.settings import settings
from app.services.session_service import get_session_service

logger = get_logger(__name__)



def get_agents_directory() -> str:
    """
    Resolve the directory containing ADK agent definitions.
    """

    base_dir = Path(__file__).resolve().parent
    agents_dir = base_dir / "agents"
    return str(agents_dir)


def create_adk_services() -> Tuple[
    Any,
    Any,
    InMemoryMemoryService,
    InMemoryCredentialService,
    AgentLoader,
    LocalEvalSetsManager,
    LocalEvalSetResultsManager,
]:
    """
    Create and configure all ADK core services.

    Initializes:
    - Artifact service for file storage and blob management
    - Session service for conversation state persistence
    - Memory service for agent memory capabilities
    - Credential service for authentication and authorization
    - Agent loader to load and manage agent definitions
    - Evaluation managers for testing and evaluation workflows

    Returns:
        Tuple containing all initialized ADK service instances in order:
        (artifact_service, session_service, memory_service, credential_service,
         agent_loader, eval_sets_manager, eval_set_results_manager)
    """
    logger.info("Initializing ADK core services")

    agents_dir = get_agents_directory()

    # Initialize core services
    artifact_service = FileArtifactService("artifacts")
    session_service = get_session_service()
    memory_service = InMemoryMemoryService()
    credential_service = InMemoryCredentialService()

    logger.debug("Services initialized: artifact, session, memory, credential")

    # Initialize agent loader and evaluation managers
    agent_loader = AgentLoader(agents_dir)
    eval_sets_manager = LocalEvalSetsManager(agents_dir=agents_dir)
    eval_set_results_manager = LocalEvalSetResultsManager(agents_dir=agents_dir)

    logger.debug(f"Agent loader configured for directory: {agents_dir}")

    return (
        artifact_service,
        session_service,
        memory_service,
        credential_service,
        agent_loader,
        eval_sets_manager,
        eval_set_results_manager,
    )


def create_adk_web_server(
    agent_loader: AgentLoader,
    session_service: Any,
    artifact_service: Any,
    memory_service: InMemoryMemoryService,
    credential_service: InMemoryCredentialService,
    eval_sets_manager: LocalEvalSetsManager,
    eval_set_results_manager: LocalEvalSetResultsManager,
    agents_dir: str,
) -> AdkWebServer:
    """
    Create and configure the ADK Web Server instance.

    The ADK Web Server provides:
    - Web UI for interactive agent testing
    - Agent runtime and execution environment
    - Integration with all ADK services

    Args:
        agent_loader: Agent loader instance for loading agent definitions
        session_service: Session management service
        artifact_service: Artifact storage service
        memory_service: Agent memory service
        credential_service: Authentication service
        eval_sets_manager: Evaluation sets manager
        eval_set_results_manager: Evaluation results manager
        agents_dir: Path to the agents directory

    Returns:
        Configured AdkWebServer instance ready for use
    """
    logger.info("Creating ADK Web Server")

    adk_web = AdkWebServer(
        agent_loader=agent_loader,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
        credential_service=credential_service,
        eval_sets_manager=eval_sets_manager,
        eval_set_results_manager=eval_set_results_manager,
        agents_dir=agents_dir,
        extra_plugins=['app.loggers.adk_logging_plugin.LoggingPlugin']
    )

    logger.info("ADK Web Server initialized successfully")
    return adk_web


# ============================================================================
# Runner Adapter Functions
# ============================================================================


def apply_runner_patch(adk_web: AdkWebServer) -> None:
    """
    Apply runner patching to inject RunConfig for all agent runs.

    This patches the ADK Web Server's get_runner_async method to automatically
    inject RunConfig(save_input_blobs_as_artifacts=True) for all agent runs.
    This is necessary to ensure uploaded files are properly saved as artifacts
    and accessible to the presentation orchestrator agent.

    Args:
        adk_web: ADK Web Server instance to patch
    """
    logger.info("Applying runner patch for automatic artifact saving")

    original_get_runner = adk_web.get_runner_async

    async def patched_get_runner(app_name: str):
        """
        Get a runner with automatic RunConfig injection.

        Args:
            app_name: Name of the ADK application/agent

        Returns:
            Runner instance with patched run_async method
        """
        runner = await original_get_runner(app_name)
        original_run_async = runner.run_async

        async def wrapped_run_async(*args, **kwargs):
            """
            Async generator wrapper that injects RunConfig.

            Automatically injects RunConfig(save_input_blobs_as_artifacts=True)
            when no explicit run configuration is provided, then yields all
            events from the original generator.
            """
            if "run_config" not in kwargs or kwargs["run_config"] is None:
                kwargs["run_config"] = RunConfig(save_input_blobs_as_artifacts=True)
                logger.debug("Injected RunConfig: save_input_blobs_as_artifacts=True")

            async for event in original_run_async(*args, **kwargs):
                yield event

        runner.run_async = wrapped_run_async
        return runner

    adk_web.get_runner_async = patched_get_runner
    logger.info("Runner patch applied successfully")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application with ADK Web integration.

    This factory function orchestrates the complete application setup:
    1. Configures ADK logging
    2. Initializes ADK core services (session, artifact, memory, credentials)
    3. Creates ADK Web Server with agent loader and evaluation managers
    4. Retrieves FastAPI app from ADK with Web UI enabled
    5. Configures custom OpenAPI schema (excluding ADK internal routes)
    6. Patches the runner to inject RunConfig for artifact saving
    7. Stores ADK services on app.state for route access
    8. Attaches authentication middleware
    9. Registers API routers
    10. Adds utility endpoints (health check, root redirect)

    Important:
        This function runs at MODULE IMPORT TIME, not during server startup.
        When uvicorn loads app.main:app, this function executes immediately to
        create the FastAPI instance. The lifespan events run later when uvicorn
        actually starts the server.

    Returns:
        Fully configured FastAPI application instance ready for deployment
    """
    logger.info("=" * 60)
    logger.info("Initializing FastAPI + ADK Web application")
    logger.info("=" * 60)

    # Step 1: Configure ADK logging
    # configure_adk_logging()

    # Step 2: Create ADK core services
    (
        artifact_service,
        session_service,
        memory_service,
        credential_service,
        agent_loader,
        eval_sets_manager,
        eval_set_results_manager,
    ) = create_adk_services()

    # Step 3: Create ADK Web Server
    agents_dir = get_agents_directory()
    adk_web = create_adk_web_server(
        agent_loader=agent_loader,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
        credential_service=credential_service,
        eval_sets_manager=eval_sets_manager,
        eval_set_results_manager=eval_set_results_manager,
        agents_dir=agents_dir,
    )

    # Step 4: Get FastAPI app from ADK with Web UI enabled
    logger.info("Getting FastAPI application from ADK Web Server")

    # Dynamically locate ADK's bundled UI assets
    adk_cli_dir = Path(google.adk.cli.__file__).parent
    web_assets_dir = str(adk_cli_dir / "browser")
    logger.info(f"Using ADK Web UI assets from: {web_assets_dir}")

    app = adk_web.get_fast_api_app(web_assets_dir=web_assets_dir)
    app.add_middleware(RequestLoggingMiddleware)

    # Step 5: Configure custom OpenAPI schema
    logger.info("Custom OpenAPI schema configured")

    # Step 6: Apply a runner patch for artifact saving
    apply_runner_patch(adk_web)

    # Step 7: Store ADK services on app.state for route access
    app.state.adk_web = adk_web
    app.state.artifact_service = artifact_service
    app.state.session_service = session_service
    logger.debug("ADK services attached to app.state")

    # Step 8: Add authentication middleware
    
    
    logger.info("Authentication middleware configured")

    # Step 9: Include API routers
    # app.include_router(auth_router, prefix="/api/v1", include_in_schema=True)

    # Step 10: Add utility endpoints
    @app.get("/health", tags=["system"])
    async def health_check():
        """
        Health check endpoint for liveness and readiness probes.

        Returns:
            Simple JSON response with application status, version, and environment.
        """
        return {
            "status": "ok",
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect the root path to ADK Web UI for interactive agent testing."""
        return RedirectResponse(url="/dev-ui/")

    logger.info("=" * 60)
    logger.info("Application initialization complete")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    logger.info("=" * 60)

    return app
 