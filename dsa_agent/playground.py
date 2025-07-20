from agent.dsa_agent import DSAAgent
from agno.playground import Playground
from api.main import app

agent = DSAAgent(user_id="playground", session_id="playground")

playground = Playground(api_app=app, agents=[agent])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("playground:app", reload=True)
