from flask import jsonify, request, Blueprint, current_app
from db.mysql_component import MySQLConnector
from core.models import (
    User,
)

import core.utils as utils

routes = Blueprint("routes", __name__)

#####################################################################
#                           REGULAR APIs                            #
#####################################################################


@routes.route("/")
def hello_world():
    # 1/0  # raises an error
    return "<p>Hello, World!</p>"


# testing betterstack
@routes.route("/test-ping-betterstack/<message>")
def test_ping_betterstack(message):
    utils.betterstack_logtail(message)
    return jsonify({"log": "Test done!", "message": message})


#####################################################################
#                           DASHBOARD APIs                          #
#####################################################################

# example api layout (DONT EXECUTE THIS EVER)

@routes.route("/example")
def example():
    
    return "DONT EXECUTE THIS"
    
    db = MySQLConnector(database="example_db")
    
    data = request.get_json()
    
    example_data = data.get("example_data", None)
    example_data2 = data.get("example_data2", None)
    
    # example sql queries
    
    # insert
    
    data = (example_data, example_data2)
    query = "INSERT INTO `example`(`example_data`, `example_data2`, `email`, `contact`) VALUES (%s, %s)"
    result, last_insert_id = db.execute_query(query, data)
    
    if result == 200:
        return jsonify({"log": "Test done!", "message": result})
    
    # update
    
    data = (example_data, example_data2)
    query = "UPDATE `example` SET `example_data`= %s WHERE example_data2 = %s"
    result = db.execute_query(query, data)
    
    if result == 200:
        return jsonify({"log": "Test done!", "message": result})
    
    # select one
    
    data = (example_data, example_data2)
    query = "SELECT example FROM `example` WHERE example_data = %s AND example_data2 = %s;"
    result = db.fetch_one(query, data)
    
    if result:
        response_data = result["example"] # to get its actual value
        result = result # to get its row
        return jsonify({"log": "Test done!", "message": result, "message2": response_data})
    else:
        return jsonify({"result": "No example data"}), 400
    
    
    # select all
    
    data = (example_data, example_data2)
    query = "SELECT example FROM `example` WHERE example_data = %s AND example_data2 = %s;"
    result = db.fetch_all(query, data)
    
    final_result = {}
    if result:
        data_id = 0
        for row in result:
            
            row_value = row["example"] # example if u need to get each value, do rest of operation in loop like assign values, calculate and such
            example_dict = {
                "example": row["example"] # another example to assign to dict 
            }
            final_result[data_id].append(example_dict)
            data_id += 1
            
            example_list = [row["example"] for row in result]
            
        result = result # to get its row
        return jsonify({"log": "Test done!", "message": result, "message2": example_dict, "message3": final_result, "message4": example_list})
    else:
        return jsonify({"result": "No example data"}), 400
        
@routes.route("/send-email", methods=["POST"])
def send_email():
    
    data = request.get_json()
    
    sender_email = data.get("sender_email", None)
    sender_name = data.get("sender_name", None)
    sender_message = data.get("sender_message", None)
    
    my_email = current_app.config["PERSONAL_MAIL"]
    subject_email = f"Portfolio Site - Email from {sender_name} ({sender_email})"
    
    payload = {"message": sender_message}
    
    message, code = utils.send_email("portfolio.html", my_email, subject_email, payload=payload)
    return jsonify({"status": message}), code

