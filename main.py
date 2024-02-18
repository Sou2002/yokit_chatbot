from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import essentials

app = FastAPI()

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON file from the request
    payload = await request.json()

    # Extracting necessary infromation
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = essentials.extract_session_id(output_contexts[0]['name'])

    def add_to_order(parameters, session_id):
        food_items = parameters['food-items']
        quantities = parameters['number']

        if len(food_items) != len(quantities):
            fulfillment_text = "Please mention food items & quantities correctly."
        else:
            food_dict = dict(zip(food_items, quantities))

            if session_id in inprogress_orders:
                current_food_item = inprogress_orders[session_id]
                current_food_item.update(food_dict)
                inprogress_orders[session_id] = current_food_item
            else:
                inprogress_orders[session_id] = food_dict

            order_str = essentials.get_str_from_food_dict(inprogress_orders[session_id])
            fulfillment_text = f"So far you have {order_str}. Do you need anything else?"

        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text})
        

    def remove_from_order(parameters, session_id):
        if session_id not in inprogress_orders:
            fulfillment_text = "Sorry could not find your order. Please try again!"
        else:
            curr_food_dict = inprogress_orders[session_id]
            remove_food = parameters['food-items']
            removed_items = []
            not_found = []

            for item in remove_food:
                if item in curr_food_dict:
                    removed_items.append(item)
                    del curr_food_dict[item]
                else:
                    not_found.append(item)

            if len(removed_items) > 0:
                fulfillment_text = f"Removed {", ".join(removed_items)} from your order."

            if len(not_found) > 0:
                fulfillment_text = f"Could not find {", ".join(not_found)} in your order."

            if len(curr_food_dict) == 0:
                fulfillment_text = "Your order is empty!"

        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text})


    def complete_order(parameters, session_id):
        if session_id not in inprogress_orders:
            fulfillment_text = "Sorry could not find your order. Please try again!"
        else:
            food_dict = inprogress_orders[session_id]
            order_id = db_helper.save_to_db(food_dict)

            if order_id == -1:
                fulfillment_text = "Sorry could not process your order. Please try again!"
            else:
                order_total = db_helper.get_total_order_price(order_id)
                fulfillment_text = f"Your order is placed. Your order id is {order_id} & order total is {order_total}."

            del inprogress_orders[session_id]

        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text})


    def track_order(parameters, session_id):
        order_id = int(parameters['number'])
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            fulfillment_text = f"The order {order_id} is {order_status}."
        else:
            fulfillment_text = f"No order found with order id: {order_id}."

        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text})
    

    intent_handler = {
        "order.add - context: ongoing-order": add_to_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "order.complete - context: ongoing-order": complete_order,
        "track.order - context: ongoing-tracking": track_order
    }

    return intent_handler[intent](parameters, session_id)