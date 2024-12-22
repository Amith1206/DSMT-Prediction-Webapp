import azure.functions as func
import datetime
import json
import logging
import pickle
import pandas as pd
import holidays
import sklearn

app = func.FunctionApp()

@app.route(route="score_model", auth_level=func.AuthLevel.ANONYMOUS)
def score_model(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Getting inputs from the request
        supplier = req.params.get('supplier')
        warehouse = req.params.get('warehouse')
        order_date_str = req.params.get('order_date')
        total_qty_str = req.params.get('total_qty')

        # Validate required parameters
        if not all([supplier, warehouse, order_date_str, total_qty_str]):
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameters. Please provide supplier, warehouse, order_date, and total_qty."}),
                status_code=400,
                mimetype="application/json"
            )

        # Parse total_qty and order_date
        try:
            total_qty = float(total_qty_str)
            order_date = datetime.datetime.strptime(order_date_str, '%Y-%m-%d')
            quarter = (order_date.month - 1) // 3 + 1
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid data format. Check total_qty and date format (YYYY-MM-DD)."}),
                status_code=400,
                mimetype="application/json"
            )

        # Create feature dictionary with ordered features
        ordered_features = [
            'total_qty',
            'is_holiday',
            'q_1', 'q_2', 'q_3', 'q_4',
            'd_Aromatico', 'd_Beans Inc.', 'd_Fair Trade AG', 'd_Farmers of Brazil', 'd_Handelskontor Hamburg',
            'w_Amsterdam', 'w_Barcelona', 'w_Hamburg', 'w_Istanbul', 'w_London', 'w_Nairobi', 'w_Naples',
            'c_Arabica', 'c_Excelsa', 'c_Liberica', 'c_Maragogype', 'c_Maragogype Type B', 'c_Robusta'
        ]

        # Initialize data dictionary with zeros
        data = {feature: [0] for feature in ordered_features}

        # Set the values
        data['total_qty'] = [total_qty]
        data['is_holiday'] = [1 if order_date.date() in holidays.Germany(years=[order_date.year]) else 0]

        # Set quarter
        data[f'q_{quarter}'] = [1]

        # Set supplier
        for s in ['Aromatico', 'Beans Inc.', 'Fair Trade AG', 'Farmers of Brazil', 'Handelskontor Hamburg']:
            if s == supplier:
                data[f'd_{s}'] = [1]

        # Set warehouse
        warehouse = warehouse.replace(' - RR', '')
        for w in ['Amsterdam', 'Barcelona', 'Hamburg', 'Istanbul', 'London', 'Nairobi', 'Naples']:
            if w in warehouse:
                data[f'w_{w}'] = [1]

        # Create DataFrame with specific column order
        payload = pd.DataFrame(data)

        # Align payload columns with the model's expected feature order
        model = pickle.load(open('./xgb_model.pkl', 'rb'))
        payload = payload[model.feature_names_in_]

        # Load and use the model
        prediction = model.predict(payload)[0]

        return func.HttpResponse(
            json.dumps({
                "message": f"Model scored successfully with total_qty: {total_qty}, supplier: {supplier}, warehouse: {warehouse}, order_date: {order_date.strftime('%Y-%m-%d')}",
                "predicted_days_late": float(prediction),
                "status_code": 200
            }),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError as e:
        # Log the feature mismatch error
        logging.error(f"Error during prediction: {e}")
        logging.error(f"Expected features: {model.feature_names_in_}")
        logging.error(f"Provided features: {list(data.keys())}")

        # Return an error response
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": str(e),
                "expected_features": model.feature_names_in_.tolist(),
                "provided_features": list(data.keys())
            }),
            status_code=400,
            mimetype="application/json"
        )

    except Exception as ex:
        # Log any other exceptions
        logging.error(f"An unexpected error occurred: {ex}")

        # Return a generic error response
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "An unexpected error occurred. Please check the logs for details."
            }),
            status_code=500,
            mimetype="application/json"
        )
