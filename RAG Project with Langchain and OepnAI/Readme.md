#### Create an .env file in the root of the project with the following contents:

        OPENAI_API_KEY="Enter your api key here"
        DB_NAME_PATH="./database/transaction.db"
        CHROMA_DB_PATH="./database/chroma_db"
        API_PORT=9001
        HOST='localhost'
        FASTAPI_URL="http://localhost:9001"


#### Install all the requirements
> pip install -r requirements.txt

#### To run the Backend (FastAPI) application
> python main.py

#### To run the Streamlit frontend application
> streamlit run frontend.py


