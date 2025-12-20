import { useState } from 'react'
import CompanySelectionModal from './CompanySelectionModal'

const CompanyInput = ({ companies, onChange }) => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleAddCompanies = (newCompanies) => {
    onChange([...companies, ...newCompanies])
  }

  const handleRemoveCompany = (index) => {
    onChange(companies.filter((_, i) => i !== index))
  }

  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Company Bucket
      </label>
      
      {/* Add Button */}
      <div className="mb-3">
        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="w-full px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-all duration-200 flex items-center justify-center space-x-2"
        >
          <span>➕</span>
          <span>Add Companies from List</span>
        </button>
      </div>

      <p className="text-sm text-gray-500 mb-3">
        Select companies from Nifty 50, Nifty 100, or Top 200 lists
      </p>

      {/* Companies list */}
      {companies.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-semibold text-gray-700">
            Selected Companies ({companies.length}):
          </p>
          <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 bg-gray-50 rounded-lg border border-gray-200">
            {companies.map((company, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 bg-primary-50 text-primary-700 px-3 py-2 rounded-lg border border-primary-200"
              >
                <span className="font-medium">{company}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveCompany(index)}
                  className="text-primary-600 hover:text-primary-800 font-bold"
                  aria-label="Remove company"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Company Selection Modal */}
      <CompanySelectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddCompanies}
        existingCompanies={companies}
      />
    </div>
  )
}

export default CompanyInput

