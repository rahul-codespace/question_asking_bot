# Questions Asking Agent

## Getting Started

Follow the instructions below to set up your virtual environment and install the required packages after cloning the repository.

### Prerequisites

Ensure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/).

### Setup

1. **Clone the repository**:

   ```bash
   git clone <url>
   cd project-name
   ```

2. **Create a virtual environment**:
   Open the terminal in the project directory and run the following command to create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:

   - **On Windows**:

     ```bash
     .venv\Scripts\activate
     ```

   - **On macOS and Linux**:

     ```bash
     source .venv/bin/activate
     ```

4. **Install the required packages**:
   With the virtual environment activated, install the required packages by running:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   Start the application by running:

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:8000/docs` to access the Swagger documentation.
