from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError

class CarSysException(Exception):
    """This is the base class for all car sys errors"""

    pass


class InvalidToken(CarSysException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(CarSysException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(CarSysException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(CarSysException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(CarSysException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(CarSysException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(CarSysException):
    """User does not have the neccessary permissions to perform an action."""

    pass


class CarNotFound(CarSysException):
    """Book Not found"""

    pass




class UserNotFound(CarSysException):
    """User Not found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass

def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: CarSysException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler



def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "detail": "User with email already exists",
                "status_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "detail": "User not found",
                "status_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        CarNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "detail": "Car not found",
                "status_code": "car_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "detail": "Invalid Email Or Password",
                "status_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "status_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "status_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "status_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status_code": "refresh_token_required",
                "detail": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status_code": "insufficient_permissions",
                "detail": "You do not have enough permissions to perform this action",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "status_code": "server_error",
                "detail": "Oops! Something went wrong",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "status_code": "server_error",
                "detail": "Oops! Something went wrong",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )