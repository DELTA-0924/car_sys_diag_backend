schema_refresh_token = {
    "type":"object",
    "properties":{
        "access_token":{"type":"string"}
    } 
}


schema_UserModel = {
  "type": "object",
  "properties": {
    "uid": {
      "type": "integer",
      "title": "Uid"
    },
    "username": {
      "type": "string",
      "title": "Username"
    },
    "email": {
      "type": "string",
      "title": "Email"
    },
    "is_verified": {
      "type": "boolean",
      "title": "Is Verified"
    },
    "password_hash": {
      "type": "string",
      "title": "Password Hash"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "title": "Created At"
    },
    "update_at": {
      "type": "string",
      "format": "date-time",
      "title": "Update At"
    }
  },
  "required": [
    "uid",
    "username",
    "email",
    "is_verified",
    "created_at",
    "update_at"
  ],
  "title": "YourModelName"
}