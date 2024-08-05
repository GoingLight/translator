from flask import jsonify

def response_template(status_code, message, data=None):
    if status_code == 200:
        return {
            "success": {
                "resut": jsonify(data),
            },
            "error": {},
        }
    elif status_code == 400 or status_code == 500:
        return {
            "success":{},
            "error": {
                "message": message,
            },
        }
    return