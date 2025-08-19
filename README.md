=========================================
       Django_SmartAPI_OHLC_DATA_Fetch
=========================================

          PROJECT DESCRIPTION
=========================================

This project is a Django-based web application that integrates with 
Angel One's Smart API to fetch **OHLC (Open, High, Low, Close)** 
stock market data. 

It allows users to securely authenticate using API keys and TOTP 
verification, then retrieve real-time OHLC candle data from Angel 
One’s trading platform.

Key Features:
- Fetches real-time OHLC data using Angel One Smart API.
- Place the Order in Real Time in Angel One 
- Secure environment configuration using `.env` file.
- Lightweight Django application, easy to set up and run locally.
- Provides JSON response for OHLC data visualization or integration.

=========================================
        STEPS TO RUN THE PROJECT LOCALLY
=========================================

1. Open the project:
   ------------------
   Open the cloned project folder in Visual Studio Code (VS Code) 
   or your preferred code editor.

2. Create the `.env` file:
   ------------------------
   Inside the project root directory, create a `.env` file and add the following:

       SMARTAPI_API_KEY=your_api_key
       SMARTAPI_CLIENT_ID=your_client_id
       SMARTAPI_USERNAME=your_client_id
       SMARTAPI_PASSWORD=your_angel_one_password
       SMARTAPI_TOTP_SECRET=generated_TOTP_SECRET_from_scanner

3. Set up the virtual environment:
   --------------------------------

   Create the virtual environment:

       python -m venv venv

   Activate the virtual environment:

       On Windows (PowerShell or CMD):
           .\venv\Scripts\activate

       On macOS/Linux (bash/zsh):
           source venv/bin/activate

5. Install required dependencies:
   -------------------------------
       pip install -r requirements.txt

6. Run the project:
   -----------------
       python manage.py runserver

8. Access the application:
   ------------------------
   Open your web browser and go to:

       http://127.0.0.1:8000

=========================================
           END OF SETUP INSTRUCTIONS
=========================================
