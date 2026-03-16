from fastapi import FastAPI
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

list_of_valid_APIkeys = ["Beer", "Beesje"] 

## Create the database model 
class Coordinates(SQLModel, table=True):
    X: float = Field(primary_key=True, description="The X coordinate of the tree")
    Y: float = Field(primary_key=True, description="The Y coordinate of the tree")
    APIkey: str = Field(index=True, description="The API key of the user adding the tree")

## database connection: the engine is what holds the connection to the database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

## create the database and tables if they don't exist yet
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

## create a database session per request
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)] 

app = FastAPI() #creates a fastAPI instance

## startup ensures the tables exist before requests start coming in.
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#set_of_trees = set()
# @app.post("/data/")
# async def add_tree(tree: Coordinates):
#     if tree.APIkey not in list_of_valid_APIkeys:
#         return {"error": "Invalid API key"}
#     set_of_trees.add((tree.X, tree.Y)) 

@app.post("/data/")
def add_tree(tree: Coordinates, session: SessionDep) -> Coordinates:
    if tree.APIkey not in list_of_valid_APIkeys:
        return {"error": "Invalid API key"}
    session.add(tree)
    session.commit()
    session.refresh(tree)
    return tree

# @app.get("/data/")
# async def get_trees():
#     return set_of_trees

@app.get("/data/")
def return_coordinates( session: SessionDep ) -> list[Coordinates]:
    trees = session.exec(select(Coordinates)).all()
    return trees