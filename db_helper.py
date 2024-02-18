import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host = 'localhost',
    user = "root",
    password = "root",
    database = 'yokit_eatery'
)

def get_order_status(order_id):
    # Cursor object
    cursor = cnx.cursor()

    # Query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Executing the query
    cursor.execute(query, (order_id,))

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    if result is not None:
        return result
    else:
        return None
    
def generate_order_id():
    # Cursor object
    cursor = cnx.cursor()

    # Query
    query = ("SELECT MAX(order_id) FROM orders")

    # Executing the query
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    if result is not None:
        return result + 1
    else:
        return 1


def insert_item(food_item, quantity, order_id):
    try:
        # Cursor object
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Commit
        cnx.commit()

        # Closing the cursor
        cursor.close()

        # print("Item inserted succesfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting item: {err}")
        return -1
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1


def insert_order_tracking(order_id, status):
    # Cursor object
    cursor = cnx.cursor()

    # Query
    query = f"INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"

    # Executing the query
    cursor.execute(query, (order_id, status))

    # Commit
    cnx.commit()

    # Closing the cursor
    cursor.close()


def save_to_db(food_dict):
    order_id = generate_order_id()

    for food_item, quantity in food_dict.items():
        flag = insert_item(food_item, quantity, order_id)

        if flag == -1:
            return -1
        
    insert_order_tracking(order_id, "in progress")
        
    return order_id


def get_total_order_price(order_id):
    # Cursor object
    cursor = cnx.cursor()

    # Query
    query = f"SELECT get_total_order_price({order_id})"

    # Executing the query
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    return result