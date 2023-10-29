from fastapi import FastAPI

from library_app.routes import auth, books, timeline, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(timeline.router)
app.include_router(users.router)
