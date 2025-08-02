# VyapaarAI – Smart Sales Prediction Tool for Small Businesses

VyapaarAI is an intelligent sales forecasting tool designed for small shopkeepers. It not only predicts future sales using machine learning but also provides key business insights like top customers, best-selling products, and daily trends. Built with a Flask backend and integrated with Twilio for smart notifications.

## Key Features

- Predicts future sales using past data (Linear Regression)
- Identifies top customers and top-selling products
- Parses CSV sales data and extracts useful metrics
- Sends prediction alerts via Twilio (SMS)
- Exposes all functionality through a simple REST API

## Tech Stack

- **Languages**: Python
- **Libraries**: Pandas, NumPy, Scikit-learn, Flask
- **API Tools**: Postman, Twilio API
- **Platform**: Localhost (can be deployed to any backend server)

## Folder Structure

```

VyapaarAI/
├── app.py          # Flask app entry point
├── model.py        # ML prediction and logic
├── utils.py        # CSV handling, top customer logic
├── twilio\_alerts.py# Twilio API integration
├── data/           # Sample sales data
└── README.md

````

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/Pihu200106/VyapaarAI.git
   cd VyapaarAI/backend
````

2. Install the required libraries:

   ```bash
   pip install flask pandas numpy scikit-learn twilio
   ```
3. Add your Twilio credentials in a `.env` or `config.py` file.
4. Run the Flask app:

   ```bash
   python app.py
   ```
5. Test endpoints using Postman or any HTTP client.

## API Endpoints

* `POST /predict`: Predict future sales from uploaded CSV
* `GET /top-customers`: Returns list of top customers
* `GET /top-products`: Returns list of top-selling products
* `POST /send-alert`: Sends prediction alert via Twilio SMS

## Future Enhancements

* Add a clean frontend with Streamlit or React
* Include authentication and user dashboard
* Improve prediction accuracy with time-series models

## Repository

[GitHub – VyapaarAI](https://github.com/Pihu200106/VyapaarAI/tree/main/backend)

Let me know if you want a short bullet point version of this for your resume too.
```
