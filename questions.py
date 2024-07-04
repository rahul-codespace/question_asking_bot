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
    "1": "User response should indicate readiness to proceed with answering questions about their company.",
    "2": "User response should contain the name of the company without any special characters or numbers.",
    "3": "User response should include the city and state where the company is located.",
    "4": "User response should indicate whether they are the owner of the company.",
    "5": "User response should provide a brief and accurate summary of their business.",
    "6": "User response should clearly identify the primary industry of the company based on the description provided.",
    "7": "User response should specify which type(s) of customers the company serves ('Consumers', 'Businesses', 'Government').",
    "8": "User response should describe the nature of the business ('Manufacturing', 'Service', 'Trade (Retail/Wholesale/Distribution)').",
    "9": "User response should state the number of employees currently on the company's payroll.",
    "10": "User response should specify the current ERP system used by the company."
}