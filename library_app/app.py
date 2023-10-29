from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from library_app.routes import auth, books, timeline, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(timeline.router)
app.include_router(users.router)


@app.get('/')
def root():
    return RedirectResponse(url='/docs')
