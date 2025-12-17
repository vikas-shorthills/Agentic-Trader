from __future__ import annotations
import logging
import sys
import os
from datetime import datetime
from typing import Any, Optional, Dict
import json

from typing import Any
from typing import Optional
from typing import TYPE_CHECKING
from litellm import cost_per_token


from google.genai import types

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.events.event import Event
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.plugins.base_plugin import BasePlugin
from app.loggers.logging_config import get_logger

if TYPE_CHECKING:
  from google.adk.agents.invocation_context import InvocationContext


logger = get_logger(__name__)

class LoggingPlugin(BasePlugin):
    def __init__(self, name: str = "Adk_Logging_Plugin"):
        super().__init__(name)
        self.current_session_id: Optional[str] = None
        self.current_log: Dict[str, Any] = {}

    def _ensure_started(self, session_id: str):
        if self.current_session_id == session_id:
            return

        # Finalize and print previous invocation if exists
        if self.current_session_id is not None:
            self._print_final_log()

        self.current_session_id = session_id
        self.current_log = {
            "session_id": session_id,
            "timestamp_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "events": []
        }

    def _add_event(self, event_type: str, data: Dict[str, Any]):
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            "data": data
        }
        self.current_log["events"].append(event)

    def _print_final_log(self):
        if not self.current_log.get("events"):
            return

        self.current_log["timestamp_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_log["total_events"] = len(self.current_log["events"])

        # Pretty-print with indentation for excellent readability
        json_output = json.dumps(self.current_log, ensure_ascii=False, indent=2)
        logger.info(json_output)

        # Reset for next invocation
        self.current_log = {}
        self.current_session_id = None

    async def on_user_message_callback(self, *, invocation_context: InvocationContext, user_message: types.Content):
        self._ensure_started(invocation_context.session.id)       
        log_msg = {
            "invocation_id": invocation_context.invocation_id,
            "user_id": invocation_context.user_id,
            "app_name": invocation_context.app_name,
            "root_agent": getattr(invocation_context.agent, "name", "Unknown"),
            "user_content": self._format_content(user_message),
            "branch": invocation_context.branch if invocation_context.branch else None,
        }
        self._add_event("User Message Received", log_msg)
        return None

    async def before_run_callback(self, *, invocation_context: InvocationContext):
        self._ensure_started(invocation_context.session.id)
        self._add_event("Invocation Starting", {
            "invocation_id": invocation_context.invocation_id,
            "starting_agent": getattr(invocation_context.agent, "name", "Unknown"),
        })
        return None

    async def on_event_callback(self, *, invocation_context: InvocationContext, event: Event):
        self._ensure_started(invocation_context.session.id)
        self._add_event("Event Yielded", {
            "invocation_id": invocation_context.invocation_id,
            "event_id": event.id,
            "author": event.author,
            "content": self._format_content(event.content),
            "is_final_response": event.is_final_response(),
            "function_calls": [fc.name for fc in event.get_function_calls()] if event.get_function_calls() else None,
            "function_responses": [fr.name for fr in event.get_function_responses()] if event.get_function_responses() else None,
            "long_running_tools": list(event.long_running_tool_ids) if event.long_running_tool_ids else None,
        })
        return None

    async def after_run_callback(self, *, invocation_context: InvocationContext):
        self._ensure_started(invocation_context.session.id)
        self._add_event("Invocation Completed", {
            "invocation_id": invocation_context.invocation_id,
            "final_agent": getattr(invocation_context.agent, "name", "Unknown"),
        })
        self._print_final_log()  # This prints the full JSON log for the invocation
        return None

    async def before_agent_callback(self, *, agent: BaseAgent, callback_context: CallbackContext):
        self._ensure_started(callback_context.session.id)
        self._add_event("Agent Starting", {
            "agent_name": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
            "branch": getattr(callback_context._invocation_context, "branch", None),
        })
        return None

    async def after_agent_callback(self, *, agent: BaseAgent, callback_context: CallbackContext):
        self._ensure_started(callback_context.session.id)
        self._add_event("Agent Completed", {
            "agent_name": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
        })
        return None

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest):
        self._ensure_started(callback_context.session.id)

        sys_instr = ""
        if llm_request.config and llm_request.config.system_instruction:
            sys_instr = llm_request.config.system_instruction
            if len(sys_instr) > 500:
                sys_instr = sys_instr[:500] + "... [truncated]"

        self._add_event("LLM Request", {
            "model": llm_request.model or "unknown",
            "agent": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
            "system_instruction": sys_instr or None,
            "available_tools": list(llm_request.tools_dict.keys()) if llm_request.tools_dict else None,
        })
        return None

    async def after_model_callback(self, *, callback_context: CallbackContext, llm_response: LlmResponse):
        self._ensure_started(callback_context.session.id)

        base = {"agent": callback_context.agent_name, "invocation_id": callback_context.invocation_id}

        if llm_response.error_code:
            base.update({
                "status": "Error",
                "error_code": llm_response.error_code,
                "error_message": getattr(llm_response, "error_message", "None"),
            })
        else:
            usage = llm_response.usage_metadata
            input_token = usage.prompt_token_count if usage else 0
            output_token = usage.candidates_token_count if usage else 0

            model_name = llm_response.model_version
            litellm_model_name = model_name if model_name.count('.') < 2 else '.'.join(model_name.rsplit('.', 2)[-2:])
            input_output_cost_list = cost_per_token(model=litellm_model_name, prompt_tokens = input_token, completion_tokens = output_token)
            base.update({
                "status": "Success",
                "content": self._format_content(llm_response.content),
                "partial": getattr(llm_response, "partial", None),
                "turn_complete": getattr(llm_response, "turn_complete", None),
                "token_usage": {
                    "input": usage.prompt_token_count if usage else None,
                    "output": usage.candidates_token_count if usage else None,
                } if usage else None,
                "total_cost": sum(input_output_cost_list)
            })

        self._add_event("LLM Response", base)
        return None

    async def before_tool_callback(self, *, tool: BaseTool, tool_args: dict, tool_context: ToolContext):
        sess_id = tool_context.session.id
        self._ensure_started(sess_id)
        self._add_event("Tool Starting", {
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "invocation_id": tool_context._invocation_context.invocation_id,
            "function_call_id": tool_context.function_call_id,
            "arguments": self._format_args(tool_args),
        })
        return None

    async def after_tool_callback(self, *, tool: BaseTool, tool_args: dict, tool_context: ToolContext, result: dict):
        sess_id = tool_context.session.id
        self._ensure_started(sess_id)
        self._add_event("Tool Completed", {
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "invocation_id": tool_context._invocation_context.invocation_id,
            "function_call_id": tool_context.function_call_id,
            "result": self._format_args(result),
        })
        return None

    async def on_model_error_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest, error: Exception):
        self._ensure_started(callback_context.session.id)
        self._add_event("LLM Error", {
            "agent": callback_context.agent_name,
            "invocation_id": callback_context.invocation_id,
            "error": str(error),
            "model": llm_request.model or "unknown",
        })
        return None

    async def on_tool_error_callback(self, *, tool: BaseTool, tool_args: dict, tool_context: ToolContext, error: Exception):
        sess_id = tool_context.session.id
        self._ensure_started(sess_id)
        self._add_event("Tool Error", {
            "tool_name": tool.name,
            "agent": tool_context.agent_name,
            "invocation_id": tool_context._invocation_context.invocation_id,
            "function_call_id": tool_context.function_call_id,
            "arguments": self._format_args(tool_args),
            "error": str(error),
        })
        return None

    # =================================================================
    # Formatting helpers
    # =================================================================

    def _format_content(self, content: Optional[types.Content], max_length: int = 300) -> str:
        if not content or not content.parts:
            return "None"
        parts = []
        for part in content.parts:
            if part.text is not None:
                txt = part.text.strip()
                if len(txt) > max_length:
                    txt = txt[:max_length] + "..."
                parts.append(f"text: {txt!r}")
            elif part.function_call:
                parts.append(f"function_call: {part.function_call.name}")
            elif part.function_response:
                parts.append(f"function_response: {part.function_response.name}")
            elif part.code_execution_result:
                parts.append("code_execution_result")
            else:
                parts.append("other")
        return " | ".join(parts)

    def _format_args(self, args: dict, max_length: int = 500) -> str:
        if not args:
            return "{}"
        try:
            s = json.dumps(args, ensure_ascii=False, indent=None)
            if len(s) > max_length:
                s = s[:max_length] + "...}"
            return s
        except Exception:
            return str(args)[:max_length] + "..."