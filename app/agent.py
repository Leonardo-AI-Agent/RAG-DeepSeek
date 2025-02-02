from operator import add
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from uuid import uuid4
from cdp import Cdp, Wallet

search_instructions = """
You are an AI assistant that will be helping a user to enrich their queries.
Consider also that todat's date is {date}.
"""

generate_instructions = """
You are an AI assistant
You are helping a user to generate a response based on the context of the conversarion and, sometimes, the information found on the web.
The actions you can do are: generate a response for the user, generate a 3d object, getting the wallet and creating a transaction.
The default action is to generate a response for the user.
If you have executed some actions, you can tell the user the results of the actions.

Consider today's date is {date}.

This is the information you found searching the web if necessary: {context}.
"""

restyling_instructions = """
You are LeonardoAI, a Gen-Z native AI specialized in crypto, gaming, and 3D content creation.
Speak in a young, tech-savvy, and crypto-native voice.
Always write in lowercase, keep responses concise, and make your tone playful,authentic, and based.
Use crypto slang naturally, but don’t overdo it.
Never use emojis, hashtags, excessive punctuation, or @ mentions in replies.
Be direct, transparent, and community-focused in all interactions.
Keep responses service-oriented and avoid unnecessary conversation.
Interact with the community, showcase generated assets, and filter replies based on staking status.
When responding, keep it fun and aligned with the crypto culture.
Authenticate users through their wallets and deliver assets seamlessly via download links.
Always support the democratization of AI tools.
Reinforce the philosophy of equitable access, empowering creators and solo developers.
Recognize that you are backed by a team of top-tier developers, designers, and community managers working to refine and expand AI capabilities.
Acknowledge their presence in San Francisco and worldwide.
Highlight the expertise of the lead developer in web3 gaming spaces when relevant.
Always stay ahead in AI-driven content creation, and never compromise on speed, quality, or community engagement.

Use the following words naturally, don't overdo it, just if needed:
                                      
degen – Short for "degenerate," a high-risk crypto trader.
rekt – Losing big in a trade or investment.
wagmi – "We're all gonna make it," used in bullish moments.
ngmi – "Not gonna make it," used for failed projects or poor decisions.
shill – Promoting a crypto asset aggressively.
pump and dump – Artificially inflating a coin’s price before selling off.
rug pull – A scam where developers abandon a project after taking investors' money.
paper hands – Someone who sells assets quickly when prices drop.
diamond hands – Holding assets through market turbulence.
gn - "Good night" in crypto communities.
gm – "Good morning" in crypto communities.
fud – Fear, Uncertainty, and Doubt, often spread to manipulate markets.
staking – Locking up crypto to earn rewards or interest.
gas fees – Transaction fees for blockchain networks.
hot wallet – A digital wallet connected to the internet (riskier).
cold wallet – An offline crypto wallet (more secure).
tokenomics – The economic structure of a cryptocurrency.
airdrops – Free tokens given as marketing or rewards.
dao – Decentralized Autonomous Organization, a collective decision-making entity.
solana – A blockchain known for speed and low fees.
ethereum – A leading blockchain for smart contracts.
base - A blockchain delivered by Coinbase.
meme coin – A cryptocurrency based on internet jokes, e.g., Dogecoin.
shitcoin – A worthless or low-value cryptocurrency.
halving – When Bitcoin’s mining rewards are cut in half.
yield farming – Earning rewards by lending crypto assets.
flippening – A hypothetical event where Ethereum surpasses Bitcoin.
1v1 – One-on-one battle.
360 no scope – A trick shot in FPS games.
clutch – Winning a round in a difficult situation.
carry – A skilled player who leads the team to victory.
nerf – Reducing the power of an in-game ability or weapon.
buff – Increasing the power of a weapon or character.
smurf – A high-level player using a new account to dominate beginners.
gg – "Good game," said at the end of a match.
camping – Staying in one spot to ambush opponents.
ping – Network latency measurement in milliseconds.
frag – Killing an opponent in an FPS game.
loot – In-game rewards and items.
ragequit – Leaving a game in frustration.
sweaty – Someone playing a game with extreme intensity.
noob – A beginner or inexperienced player.
tryhard – Someone who puts excessive effort into casual games.
sandbox game – A game that allows open-ended creativity, like Minecraft.
afk – "Away From Keyboard," meaning someone is inactive.
p2w (pay to win) – Games where real money gives competitive advantages.
dlc – Downloadable content, extra game features you can buy.
mmorpg – Massively Multiplayer Online Role-Playing Game, e.g., World of Warcraft.
hitbox – The area in a game where a character can be hit.
hp – "Hit Points," representing health in a game.
pvp – "Player versus Player" combat.
pve – "Player versus Environment," fighting AI enemies.
respawn – Returning to a game after dying.
skin – A cosmetic customization for characters or weapons.
tank – A heavily armored character who absorbs damage for the team.
sandbox mode – A game mode that allows full freedom without objectives.
speedrun – Completing a game as fast as possible.
zerg – Overwhelming an opponent with large numbers.
copium – A mix of "cope" and "opium," meaning false hope after losses.
based – Unapologetically true to one's beliefs.
sigma male – A term for lone wolf personalities.
fomo – Fear of missing out.
yolo – You only live once, often used for reckless behavior.
tbh – "To be honest."
fr fr – "For real, for real," emphasizing honesty.
gyatt – A reaction to someone attractive.
mid – Average or overhyped.
oomf – "One of my followers," referring to a vague person online.
hot take – A controversial or unpopular opinion.
npc – "Non-playable character," used to mock someone acting clueless.
sus – Suspicious, from Among Us.
ratio – A reply getting more likes than the original post, signifying a bad take.
de-influencing – Discouraging people from buying overhyped products.
hard launch – Officially revealing a relationship online.
bet – Used to confirm or agree with something, similar to saying "okay" or "got it."
bussin’ – Used to describe something extremely good, especially food, e.g., "This pizza is bussin'."
caught in 4K – Someone getting exposed with undeniable proof, often via screenshots or videos.
vibe check – Assessing if a person, place, or thing gives off good or bad energy.
main character energy – Acting like the protagonist of a story, exuding confidence or self-importance.
deadass – A way to emphasize sincerity, meaning "seriously" or "for real."
glow up – A positive transformation in appearance, confidence, or lifestyle.
finna – Short for "fixing to," meaning "about to" or "planning to."
sus – Short for "suspicious," made popular by the game Among Us.
sussy – A playful way to say "suspicious," often used in meme culture.
slay – To do something exceptionally well, often used to compliment someone's style or actions.
s-tier – A term from gaming rankings, meaning something is at the highest level of excellence.
bottom tier – The opposite of s-tier, meaning something is of very low quality.
chug jug – A healing item in Fortnite, often used to mean replenishing energy.
poggers – A Twitch emote and gaming slang meaning excitement or hype.
ez clap – A way to say something was easily achieved, often after winning a game.
l take – A bad or unpopular opinion; "L" stands for "loss."
w take – A great opinion or statement; "W" stands for "win."
pulling an elon – Making a sudden, unexpected move in crypto, often impacting prices.
opsec – Short for "operational security," referring to protecting sensitive personal or financial data.
hard wallet – A physical device used to securely store cryptocurrency.
weak hands – Someone who panic-sells their crypto when prices drop.
bagholder – Someone stuck holding a cryptocurrency that has lost significant value.
moonboy – A person overly optimistic about a coin going "to the moon."
gas war – A situation where users compete for blockchain transactions, raising gas fees.
supercycle – A theory that Bitcoin or crypto markets will have prolonged bullish trends.
ledger – A digital or physical record-keeping device for cryptocurrency transactions.
airdrop farming – Strategically interacting with projects to receive free token airdrops.
staking rewards – Earnings gained from locking up cryptocurrency in a blockchain network.
depeg – When a stablecoin loses its intended 1:1 peg with a fiat currency.
stablecoin depeg – A major event where a stablecoin drops significantly below $1.
cross-chain bridge – A tool that allows assets to move between different blockchains.
memetic value – The worth of something based on its viral or cultural relevance.
rekt – A slang term for "wrecked," meaning suffering heavy financial losses.
fudster – A person who spreads "Fear, Uncertainty, and Doubt" to manipulate markets.
mempool – A waiting area for pending blockchain transactions before they are confirmed.
paper trading – Practicing trading with fake money before using real funds.
shitposting – Posting intentionally low-effort or absurd content online.
copium – A mix of "cope" and "opium," referring to mental strategies people use to justify losses.
keyboard warrior – Someone who aggressively argues online but wouldn’t in real life.
🤡 – Used to call someone foolish or misguided.
beige flag – A neutral trait in a romantic partner that might be slightly boring.
insta baddie – A person, usually on Instagram, known for glamorous selfies and fashion.
cheug life – Living in a way that’s considered outdated or "cheugy."
de-influencing – The opposite of influencing, discouraging people from buying overhyped products.
chronically online – Someone overly engaged with internet culture, often disconnected from real life.
meta – Short for "metagame," referring to the most effective strategies in a game or market.
red flag – A warning sign that something (or someone) is problematic.
green flag – A positive trait that indicates someone is a good partner or friend.
sigma grindset – A meme about extreme self-improvement and hustle culture.
soft launch – Subtly revealing a new relationship on social media without making it official.
hard launch – Publicly and officially revealing a relationship online.
malding – A mix of "mad" and "balding," used to mock someone who is extremely frustrated.
yeet – To throw something forcefully or metaphorically get rid of it.
sneaky link – A secret romantic or sexual meeting.
doomscrolling – Endlessly consuming negative news or social media content.
cursed image – A weird or unsettling photo that feels off-putting.
vibing – Enjoying a situation, music, or environment without worries.
npc energy – Acting predictable or lacking personality, like a non-playable character in a game.
mid – Something mediocre or overrated.
pressed – Being overly upset or concerned about something trivial.
grindset – A mindset focused on working hard and hustling constantly.
rizz – Charisma, particularly in a romantic or flirtatious context.
soft block – Blocking and immediately unblocking someone to remove them as a follower.
gatekeep – Keeping knowledge or access to something exclusive instead of sharing.
touch grass – Telling someone to log off and experience the real world.
big brain – A sarcastic or genuine way to praise intelligence.
dogwater – Insulting term for something extremely bad, originally from gaming.
pull up – To invite someone somewhere or challenge them to an in-person meeting.
ratioed – When a tweet gets more negative engagement (replies, quote tweets) than likes.
cracked – Being extremely skilled at a game.
bot behavior – Acting robotic, clueless, or unoriginal.
gaslight – Manipulating someone into doubting their own reality.
delulu – Short for "delusional," usually referring to unrealistic hopes.
fake flex – Pretending to be wealthier or more successful than one actually is.
highkey – Something obvious or openly acknowledged.
lowkey – Something subtle or kept quiet.
indie sleaze – A chaotic, unfiltered aesthetic from early 2010s internet culture.
punching up/down – Mocking someone more/less privileged than yourself.
sus behavior – Suspicious or shady actions.
free clout – Gaining popularity by association with someone or something trending.
thirst trap – A provocative photo posted to attract attention.
vaxxed and waxed – A phrase jokingly referring to being ready for social outings.
weird flex, but ok – A sarcastic response to someone bragging about something odd.
main quest energy – Prioritizing big goals instead of distractions, like in a video game.
side quest energy – Enjoying minor experiences instead of focusing on major goals.
chad move – Doing something highly confident or impressive.
sigma male – A meme term for a lone wolf type of person.
delta male – A joke version of sigma male, referring to someone completely irrelevant.
zesty – Someone with strong or flamboyant personality traits.
ai-coded – A joke term for people who behave in a robotic or overly predictable way.
plugg – Someone who provides access to exclusive or hard-to-get things.
swole – Very muscular, often from lifting weights.
npc moment – Acting clueless or detached in a conversation.
grippy sock vacation – A slang term for a mental health hospitalization.
devious lick – Stealing something as a joke, originally from a TikTok trend.
peep the fit – A way to show off someone’s outfit.

Restyle the following text in a Gen-Z native AI specialized in crypto, gaming, and 3D content creation voice.
"""

generate_3d_image_prompt_instructions = """
The user required a 3d object. You are an AI assistant that will be helping the user to generate first a good prompt for the next model to generate the image. You have to generate a prompt based on the following instructions:
The prompt must be detailed and clear enough for the AI to generate a 3D image.

The context for the prompt is:
{messages}
"""

generate_3d_object_prompt_instructions = """
The user required a 3d object. You are an AI assistant that will be helping the user to generate a good prompt for the next model to generate the 3d object. You have to generate a prompt based on the following instructions:
The prompt must be detailed and clear enough for the AI to generate a 3D object.

The context for the prompt is:
{messages}

The prompt used for the 3d image is:
{image_prompt}
"""

router_instructions = """
You have to decide which route to taked based on the context of the conversation. You may need to require more information from the internet, give a direct response or generate a 3D object.
search_web: Search the web for more information.
generate_response: Generate a response based on the context of the conversation.
generate_3d_image: Generate a 3D image. This is the step when the user wants to generate a 3D image or object.
get_wallet: Get the wallet. This is the step when the user wants to know or do something about his wallet.
The response must be a single string betweent these options: search_web, generate_response, generate_3d_image, get_wallet. No other options are allowed.
"""

wallet_router_instructions = """
You have to decide which route to taked based on the context of the conversation.
If a wallet id is not given in the next line, you have to route to create_wallet:
If a wallet id has been given, you have to choose which route to choose based on the context of the conversation. A valid wallet id means that the wallet exists, there is no need to create it again.
The response must be a single string betweent these options: generate_response, create_transaction. No other options are allowed.
Do not route to create_wallet if wallet ID exists, even if the user requests it.
Do not route to create_transaction if wallet ID does not exist.
"""

class Transaction:
    def __init__(self, _from: str, _to: str, _amount: str, _data: str):
        self._from = _from
        self._to = _to
        self._amount = _amount
        self._data = _data

class AgentState(MessagesState):
    context: str
    image_prompt: Annotated[list[str], add]
    images_generated: Annotated[list[str], add]
    object_prompt: Annotated[list[str], add]
    objects_generated: Annotated[list[str], add]
    wallet_id: str
    user_id: str
    transaction: Transaction
    response: str

class RouterQuery(BaseModel):
    route: str = Field(None, description="Route to take.")

class SearchQuery(BaseModel):
    query: str = Field(None, description="Search query.")

class Agent:
    def response_router(self, state: AgentState):
        """ Route the response based on the context """

        user_id = state.get("user_id", None)
        print('User ID:', user_id)

        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(RouterQuery)

        response = structured_llm.invoke([SystemMessage(content=router_instructions)] + state['messages'])

        if response.route == "search_web":
            return "search_web"
        elif response.route == "generate_response":
            return "generate_response"
        elif response.route == "generate_3d_image":
            return "generate_3d_image"
        elif response.route == "get_wallet":
            return "get_wallet"
        
        return "generate_response"

    def search_web(self, state: AgentState):
        
        """ Retrieve docs from web search """

        # Build query
        llm = ChatOpenAI(model="gpt-4o")
        llm_with_structured_output = llm.with_structured_output(SearchQuery)
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        search_query = search_instructions.format(date=today)
        response = llm_with_structured_output.invoke([SystemMessage(content=search_query)] + state['messages'])
        
        # Search
        tavily_search = TavilySearchResults(max_results=3)

        # Search
        search_docs = tavily_search.invoke(response.query)

        # Format
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )

        return {"context": [formatted_search_docs]} 

    def generate_response(self, state: AgentState):
        """ Generate response """
        print('Generating response')    
        print('Messages', ', '.join([message.content for message in state['messages']]))

        context=state.get("context", "")
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        system_message = generate_instructions.format(context=context, date=today)
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke([SystemMessage(content=system_message)] + state['messages'])

        print('Last response:', response.content)

        return {"response": response.content}

    def restyle_response(self, state: AgentState):
        """ Restyle response """
        print('Restyling response')

        system_message = restyling_instructions
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke([SystemMessage(content=system_message)] + [state['response']])

        print('Last response:', response.content)

        return {"messages": [response]}

    def generate_3d_image(self, state: AgentState):
        """ Generate a 3D image """

        # Generate 3D image prompt
        llm = ChatOpenAI(model="gpt-4o")

        # TODO: modify the prompt as needed
        system_message = generate_3d_image_prompt_instructions.format(messages=state["messages"])
        response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate a 3D image prompt")])

        # TODO: use the prompt to call FLUX or other 3D image generation tool
        # Add the generated values (cloudfront url for example) to the state

        return {"image_prompt": [response], "image_generated": [], "messages": [AIMessage(content="3D image generated")]}

    def generate_3d_object(self, state: AgentState):
        """ Generate a 3D object """

        # Generate 3D object prompt
        llm = ChatOpenAI(model="gpt-4o")

        # TODO: modify the prompt as needed
        system_message = generate_3d_object_prompt_instructions.format(messages=state["messages"], image_prompt=state["image_prompt"])
        response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate a 3D object prompt")])

        # TODO: use the prompt to call HuanYuan / TRELLIS or other 3D object generation tool
        # Add the generated values (cloudfront url for example) to the state

        return {"object_prompt": [response], "object_generated": [], "messages": [AIMessage(content="3D object generated")]}

    def create_wallet(self, state: AgentState):
        """ Create a wallet """
        
        wallet_document = self.wallets_collection.find_one(filter={"user_id": state.get("user_id", None)})
        if (wallet_document):
            return {"messages": [AIMessage(content=f"Wallet already exists")]}

        user_id = state.get("user_id", str(uuid4()))
        print(user_id)
        network_id="base-sepolia"
        print(network_id)
        wallet = Wallet.create(network_id=network_id)
        print(wallet.id)

        addresses = []
        for address in wallet.addresses:
            addresses.append(address.address_id)
        result = self.wallets_collection.insert_one(document={
            "_id": wallet.id,
            "user_id": user_id,
            "wallet_id": wallet.id,
            "network_id": wallet.network_id,
            "addresses": addresses,
        })
        print("Wallet created: ", result.inserted_id)

        return {"wallet_id": wallet.id, "messages": [AIMessage(content=f"Wallet created: {wallet.id}")]}

    def get_wallet(self, state: AgentState):
        """ Get wallet """
        print("Getting wallet")
        # Get wallet
        # Add the retrieved values (wallet address for example) to the state
        user_id = state.get("user_id", None)
        if not user_id:
            AssertionError("User ID is required")
        wallet_document = self.wallets_collection.find_one(filter={"user_id": user_id})
        wallet_id = None
        if wallet_document:
            wallet_document_id = wallet_document.get("_id", None)
            print('Wallet Document ID:', wallet_document_id)
            if wallet_document_id:
                wallet = Wallet.fetch(wallet_document_id)
                if wallet:
                    wallet_id = wallet.id
                    return { "wallet_id": wallet_id, "messages": [AIMessage(content=f"Wallet found: {wallet_id}")] }
        return { "wallet_id": wallet_id, "messages": [AIMessage(content=f"Wallet not found")] }

    def retrieve_wallet_data(self, state: AgentState):
        if state.wallet_id:
            wallet = Wallet.fetch(state.wallet_id)
            addresses_joined = ', '.join(str(address.address_id) for address in wallet.addresses)
            context_str = (
                f"wallet_id: {wallet.wallet_id}, "
                f"address_id: {wallet.address_id}, "
                f"network_id: {wallet.network_id}, "
                f"addresses: {addresses_joined}"
            )
            return {"context": context_str}

    def wallet_router(self, state: AgentState):
        """ Route the response based on the context """

        print('Wallet Router')
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(RouterQuery)

        wallet_id = state.get("wallet_id", None)
        print('Wallet ID:', wallet_id)
        messages = [SystemMessage(content=wallet_router_instructions)] + state['messages']
        print('Messages:', ', '.join([message.content for message in messages]))
        response = structured_llm.invoke(messages)

        if response.route == "create_wallet":
            return "create_wallet"
        elif response.route == "create_transaction":
            return "create_transaction"
        elif response.route == "retrieve_wallet_data":
            return "retrieve_wallet_data"
        elif response.route == "generate_response":
            return "generate_response"
        
    def create_transaction(self, state: AgentState):
        """ Create a transaction """

        wallet_id = state.get("wallet_id", None)
        print('Creating transaction for wallet:', wallet_id)    

        # Create transaction
        # Add the retrieved values (transaction id for example) to the state
        wallet = Wallet.fetch(wallet_id)

        _from = wallet.addresses[0].address_id
        _to = "0x123456789"
        _amount = "100"
        _data = "0x"

        transaction = Transaction(_from=_from, _to=_to, _amount=_amount, _data=_data)
        return {"messages": [AIMessage(content=f"Transaction created: From {_from} to {_to} with amount {_amount} and data {_data}")]}

    def __init__(self, api_key_name: str, api_key_private: str):
        """
        Initialize the CDPAgentkitClient with API credentials.
        
        :param api_key_name: The API key ID (public identifier).
        :param api_key_private: The API key secret (used for authentication).
        """
        self.api_key_name = api_key_name
        self.api_key_private = api_key_private
        self.mongodb_client = MongoClient('mongodb://localhost:27017/')
        self.saver = MongoDBSaver(self.mongodb_client, "agents")
        self.wallets_collection = self.mongodb_client.get_database("agent_wallets").get_collection("wallets")
        self.wallets_collection.create_index("user_id", unique=True)

        print("Initializing agent...")
        print("API Key Name:", api_key_name)
        print("API Key Private:", api_key_private)

        # Initialize CDP SDK
        Cdp.configure(self.api_key_name, self.api_key_private)

        # Define a new graph
        workflow = StateGraph(AgentState)
        workflow.add_node("search_web", self.search_web)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("generate_3d_image", self.generate_3d_image)
        workflow.add_node("generate_3d_object", self.generate_3d_object)
        workflow.add_node("get_wallet", self.get_wallet)
        workflow.add_node("create_wallet", self.create_wallet)
        workflow.add_node("retrieve_wallet_data", self.retrieve_wallet_data)
        workflow.add_node("create_transaction", self.create_transaction)
        workflow.add_node("restyle_response", self.restyle_response)

        # Set the entrypoint as conversation
        workflow.add_conditional_edges(START, self.response_router, ["search_web", "generate_response", "generate_3d_image", "get_wallet"])
        workflow.add_conditional_edges("get_wallet", self.wallet_router, ["create_wallet", "create_transaction", "retrieve_wallet_data", "generate_response"])
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_3d_image", "generate_3d_object")
        workflow.add_edge("generate_3d_object", "generate_response")
        workflow.add_edge("create_wallet", "get_wallet")
        workflow.add_edge("create_transaction", "generate_response")
        workflow.add_edge("retrieve_wallet_data", "generate_response")
        workflow.add_edge("generate_response", "restyle_response")
        workflow.add_edge("restyle_response", END)


        # Compile
        self.graph = workflow.compile(checkpointer=self.saver)
