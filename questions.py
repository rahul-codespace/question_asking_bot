# Define the questions dictionary
questions_dic = {
    "1": "Ask Permission: Welcome User! And say before we get started, I need to ask you a few questions about your company. Are you ready to proceed?",
    "2": "Company Name: Ask for the name of the company.",
    "3": "Company Location: Ask for the city and state where the company is located.",
    "4": "IsOwner: Ask if the user is the owner of the company.",
    "5": "Business Description: Ask the user to provide a brief summary of their business.",
    "6": "Primary Industry: Determine the primary industry based on the given business description. If unclear, ask the user to specify.",
    "7": "CustomerType: Ask which type of customers the company serves: 'Consumers', 'Businesses', 'Government'.",
    "8": "Business Nature: Ask about the nature of the business: 'Manufacturing', 'Service', 'Trade (Retail/Wholesale/Distribution)'.",
    "9": "No of Employee Payroll: Ask how many employees are on the company's payroll.",
    "10": "ERP System: Ask which ERP system the company is currently using."
}

# Define QuestionVerifier dictionary that maps question numbers to evaluation criteria

evaluation_criteria_dic = {
    "1": "The user should respond with 'Yes' or 'No'.",
    "2": "The company name should be a valid string with maximum length of 50 characters.",
    "3": "The company location should be contained in a valid city, state format. For example, 'New York, NY'.",
    "4": "The user should respond with 'Yes' or 'No'.",
    "5": "The business description should be a valid string that describes the business in a few sentences. or minimum length of in one sentence.",
    "6": "The primary industry should be a valid industry type or 'Unspecified'.",
    "7": "The customer type should be 'Consumers', 'Businesses', or 'Government'.",
    "8": "The business nature should be 'Manufacturing', 'Service', or 'Trade'.",
    "9": "The number of employees should be a valid integer.",
    "10": "The ERP system should be a valid system name of any ERP System."
}
