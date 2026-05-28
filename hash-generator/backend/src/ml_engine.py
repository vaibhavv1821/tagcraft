# backend/src/ml_engine.py — TagCraft v4.0
# ML Engine with 200+ hashtags across all major topics

import re
import numpy as np
from collections import Counter

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_OK = True
except ImportError:
    SENTENCE_TRANSFORMERS_OK = False

try:
    from keybert import KeyBERT
    KEYBERT_OK = True
except ImportError:
    KEYBERT_OK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False


HASHTAG_DB = [
    
    # ── Locations / Places ──
("#iceland",         "Iceland travel nordic cold aurora borealis northern lights",    ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#europe",          "Europe travel continent explore cities culture history",         ["travel"],           ["instagram","youtube","twitter"]),
("#northernlights",  "northern lights aurora borealis Iceland Norway sky night",       ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#scandinavia",     "Scandinavia Nordic Norway Sweden Denmark Finland travel",        ["travel"],           ["instagram","youtube","twitter"]),
("#norway",          "Norway fjords nature outdoor adventure Scandinavia travel",      ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#switzerland",     "Switzerland Alps mountains snow travel Europe scenic nature",    ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#bali",            "Bali Indonesia travel beach temple culture tropical paradise",   ["travel"],           ["instagram","youtube","twitter"]),
("#thailand",        "Thailand travel Asia beach temple food culture tropical",        ["travel"],           ["instagram","youtube","twitter"]),
("#paris",           "Paris France Eiffel Tower Europe travel romantic culture",       ["travel"],           ["instagram","youtube","twitter"]),
("#japan",           "Japan travel culture anime food Tokyo Kyoto sakura tradition",   ["travel"],           ["instagram","youtube","twitter"]),
("#maldives",        "Maldives island beach tropical ocean water bungalow luxury",     ["travel"],           ["instagram","youtube","twitter"]),
("#goa",             "Goa India beach party sunset sea travel vacation holiday",       ["travel","india"],   ["instagram","youtube","twitter"]),
("#kerala",          "Kerala India backwaters nature green God's own country travel",  ["travel","india"],   ["instagram","youtube","twitter"]),
("#rajasthan",       "Rajasthan India desert palace culture heritage fort travel",     ["travel","india"],   ["instagram","youtube","twitter"]),
("#himalayas",       "Himalayas mountain trek India Nepal snow peak altitude base",    ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#leh",             "Leh Ladakh India mountain bike road trip adventure cold",        ["travel","outdoor"], ["instagram","youtube","twitter"]),

# ── Seasons / Weather ──
("#snow",            "snow winter cold mountain white landscape ski outdoor",          ["outdoor","nature"], ["instagram","youtube","twitter"]),
("#winter",          "winter cold snow season outdoor landscape cozy",                 ["outdoor","nature"], ["instagram","youtube","twitter"]),
("#summer",          "summer heat beach vacation holiday outdoor fun sun",             ["travel","outdoor"], ["instagram","youtube","twitter"]),
("#monsoon",         "monsoon rain India season green nature outdoor travel",          ["nature","india"],   ["instagram","youtube","twitter"]),

# ── Activities ──
("#skiing",          "skiing snow mountain winter sport slope outdoor adventure",      ["outdoor","fitness"], ["instagram","youtube","twitter"]),
("#scubadiving",     "scuba diving underwater ocean sea marine life adventure",        ["outdoor","travel"],  ["instagram","youtube","twitter"]),
("#surfing",         "surfing wave ocean beach sport outdoor water adventure",         ["outdoor","fitness"], ["instagram","youtube","twitter"]),
("#paragliding",     "paragliding fly sky outdoor adventure sport mountain",           ["outdoor","fitness"], ["instagram","youtube","twitter"]),
("#skydiving",       "skydiving jump plane extreme sport outdoor adventure thrill",    ["outdoor","fitness"], ["instagram","youtube","twitter"]),
    
    # ── Outdoor / Hiking / Nature ──
    ("#hiking",           "hiking trail mountain outdoor trekking walk nature path",         ["outdoor","fitness"], ["instagram","youtube","twitter"]),
    ("#trekking",         "trekking mountain trail outdoor adventure hiking expedition",     ["outdoor","fitness"], ["instagram","youtube","twitter"]),
    ("#mountaineering",   "mountaineering climbing peak summit outdoor adventure",           ["outdoor","fitness"], ["instagram","youtube","twitter"]),
    ("#outdoors",         "outdoors nature fresh air adventure explore hiking camping",      ["outdoor","nature"],  ["instagram","youtube","twitter"]),
    ("#adventure",        "adventure outdoor explore nature thrill excitement journey",      ["outdoor","travel"],  ["instagram","youtube","twitter"]),
    ("#mountains",        "mountains peak summit landscape scenic nature beauty altitude",   ["outdoor","nature"],  ["instagram","youtube","twitter"]),
    ("#camping",          "camping tent outdoor nature wilderness survival fire forest",     ["outdoor","nature"],  ["instagram","youtube","twitter"]),
    ("#naturephotography","nature photography landscape wildlife outdoor scenic beauty",     ["outdoor","photo"],   ["instagram","twitter","youtube"]),
    ("#hikingadventure",  "hiking adventure trail mountain outdoor explore discover",        ["outdoor","fitness"], ["instagram","twitter","youtube"]),
    ("#mountainlife",     "mountain life outdoor adventure nature scenic peak altitude",     ["outdoor","nature"],  ["instagram","twitter","youtube"]),
    ("#trailrunning",     "trail running outdoor fitness mountain endurance cardio",         ["outdoor","fitness"], ["instagram","twitter","youtube"]),
    ("#exploreoutdoors",  "explore outdoors nature adventure travel discover wilderness",    ["outdoor","travel"],  ["instagram","twitter","youtube"]),
    ("#wilderness",       "wilderness nature outdoor wild forest survival adventure",        ["outdoor","nature"],  ["instagram","twitter","youtube"]),
    ("#summit",           "summit peak mountain top climbing achievement outdoor",           ["outdoor","fitness"], ["instagram","twitter","youtube"]),
    ("#backpacker",       "backpacker travel adventure outdoor nature explore solo",        ["outdoor","travel"],  ["instagram","youtube","twitter"]),
    ("#landscape",        "landscape nature scenery photography outdoor beauty scenic",     ["outdoor","photo"],   ["instagram","twitter","youtube"]),
    ("#forest",           "forest trees nature woodland outdoor green hiking",              ["outdoor","nature"],  ["instagram","twitter","youtube"]),
    ("#sunset",           "sunset golden hour sky nature beauty photography outdoor",       ["outdoor","photo"],   ["instagram","twitter","youtube"]),
    ("#sunrise",          "sunrise morning sky nature beauty photography outdoor golden",   ["outdoor","photo"],   ["instagram","twitter","youtube"]),
    ("#oceanview",        "ocean view sea beach water nature scenic photography",           ["outdoor","travel"],  ["instagram","twitter","youtube"]),

    # ── AI / ML ──
    ("#artificialintelligence","artificial intelligence machine learning AI systems automation",["ai","tech"],["linkedin","twitter","instagram"]),
    ("#machinelearning",  "machine learning algorithms data models training prediction",    ["ai","tech"], ["linkedin","github","twitter"]),
    ("#deeplearning",     "deep learning neural networks layers training classification",   ["ai","tech"], ["linkedin","github","twitter"]),
    ("#datascience",      "data science analysis statistics insights visualization",        ["ai","tech"], ["linkedin","github","twitter"]),
    ("#neuralnetworks",   "neural networks layers neurons deep learning training",          ["ai","tech"], ["linkedin","github"]),
    ("#generativeai",     "generative AI image text generation creative content",           ["ai","tech"], ["linkedin","twitter","instagram"]),
    ("#llm",              "large language models GPT transformer NLP text generation",     ["ai","tech"], ["linkedin","github","twitter"]),
    ("#promptengineering","prompt engineering LLM AI chatbot instructions optimization",   ["ai","tech"], ["linkedin","twitter"]),
    ("#mlops",            "machine learning operations deployment pipeline monitoring",     ["ai","tech"], ["linkedin","github"]),
    ("#nlp",              "natural language processing text understanding sentiment",       ["ai","tech"], ["linkedin","github","twitter"]),
    ("#computervision",   "computer vision image recognition object detection OpenCV",     ["ai","tech"], ["linkedin","github","twitter"]),
    ("#chatgpt",          "ChatGPT OpenAI conversational AI assistant language model",     ["ai","tech"], ["twitter","linkedin","instagram"]),
    ("#aitools",          "AI tools productivity automation software applications",         ["ai","tech"], ["twitter","linkedin","instagram"]),
    ("#tensorflow",       "TensorFlow deep learning model training Google framework",      ["ai","code"], ["github","linkedin","twitter"]),
    ("#pytorch",          "PyTorch deep learning neural network model training",           ["ai","code"], ["github","linkedin","twitter"]),

    # ── Programming ──
    ("#python",           "Python programming language scripting automation data",         ["code","tech"], ["github","linkedin","twitter"]),
    ("#javascript",       "JavaScript web development frontend backend dynamic",           ["code","tech"], ["github","linkedin","twitter"]),
    ("#typescript",       "TypeScript typed JavaScript web development large apps",        ["code","tech"], ["github","linkedin","twitter"]),
    ("#reactjs",          "React JavaScript UI components frontend web SPA hooks",         ["code","tech"], ["github","linkedin","twitter"]),
    ("#nodejs",           "Node.js server-side JavaScript backend API event-driven",       ["code","tech"], ["github","linkedin","twitter"]),
    ("#django",           "Django Python web framework REST API backend MVC",              ["code","tech"], ["github","linkedin"]),
    ("#flask",            "Flask Python micro web framework API REST lightweight",         ["code","tech"], ["github","linkedin"]),
    ("#fastapi",          "FastAPI Python async REST API framework modern",                ["code","tech"], ["github","linkedin"]),
    ("#golang",           "Go Golang programming language systems backend concurrent",     ["code","tech"], ["github","linkedin","twitter"]),
    ("#rust",             "Rust systems programming language memory safety performance",   ["code","tech"], ["github","linkedin","twitter"]),
    ("#java",             "Java programming enterprise backend Spring framework",          ["code","tech"], ["github","linkedin"]),
    ("#cpp",              "C++ systems programming performance games graphics",            ["code","tech"], ["github","linkedin"]),
    ("#coding",           "coding programming software development build create",          ["code","tech"], ["github","linkedin","twitter","instagram"]),
    ("#programming",      "programming software development code project build",           ["code","tech"], ["github","linkedin","twitter","instagram"]),
    ("#developer",        "developer software engineer programmer build deploy",           ["code","tech"], ["github","linkedin","twitter"]),
    ("#100daysofcode",    "100 days of code daily programming challenge community",        ["code","community"], ["twitter","instagram","linkedin"]),
    ("#opensource",       "open source community collaboration GitHub contribute",         ["code","community"], ["github","twitter","linkedin"]),
    ("#buildinpublic",    "building in public project startup developer share progress",   ["code","startup"], ["twitter","linkedin"]),
    ("#sideproject",      "side project developer build coding weekend personal hack",     ["code","startup"], ["twitter","linkedin","github"]),
    ("#indiehacker",      "indie hacker bootstrap startup product build solo founder",    ["code","startup"], ["twitter","linkedin"]),

    # ── Web Development ──
    ("#webdev",           "web development frontend backend full stack HTML CSS JS",      ["web","code"], ["github","linkedin","twitter"]),
    ("#webdevelopment",   "web development HTML CSS JavaScript responsive design",         ["web","code"], ["github","linkedin","twitter"]),
    ("#frontend",         "frontend development UI UX CSS HTML JavaScript interface",     ["web","code"], ["github","linkedin","twitter"]),
    ("#backend",          "backend development server API database logic architecture",    ["web","code"], ["github","linkedin","twitter"]),
    ("#fullstack",        "full stack development frontend backend database together",     ["web","code"], ["github","linkedin","twitter"]),
    ("#html",             "HTML markup web page structure content semantics",              ["web","code"], ["github","linkedin","twitter"]),
    ("#css",              "CSS styling design layout responsive animation web",            ["web","code"], ["github","linkedin","twitter","instagram"]),
    ("#api",              "API REST GraphQL endpoint integration service interface",       ["web","code"], ["github","linkedin","twitter"]),
    ("#restapi",          "REST API HTTP endpoints JSON web service architecture",         ["web","code"], ["github","linkedin","twitter"]),
    ("#graphql",          "GraphQL API query language flexible data fetch schema",         ["web","code"], ["github","linkedin","twitter"]),

    # ── DevOps / Cloud ──
    ("#devops",           "DevOps CI CD pipeline deployment automation infrastructure",   ["devops","cloud"], ["github","linkedin","twitter"]),
    ("#docker",           "Docker container deployment microservices image registry",      ["devops","cloud"], ["github","linkedin","twitter"]),
    ("#kubernetes",       "Kubernetes container orchestration deployment scaling",         ["devops","cloud"], ["github","linkedin","twitter"]),
    ("#aws",              "AWS Amazon cloud computing services deployment serverless",     ["devops","cloud"], ["linkedin","twitter","github"]),
    ("#azure",            "Microsoft Azure cloud computing platform enterprise",           ["devops","cloud"], ["linkedin","twitter","github"]),
    ("#gcp",              "Google Cloud Platform computing services BigQuery",             ["devops","cloud"], ["linkedin","twitter","github"]),
    ("#cloudcomputing",   "cloud computing scalable infrastructure services SaaS",        ["devops","cloud"], ["linkedin","twitter"]),
    ("#cicd",             "CI CD continuous integration deployment pipeline automation",  ["devops","cloud"], ["github","linkedin","twitter"]),
    ("#terraform",        "Terraform infrastructure as code IaC automation cloud",        ["devops","cloud"], ["github","linkedin","twitter"]),
    ("#githubactions",    "GitHub Actions CI CD workflow automation pipeline deploy",     ["devops","cloud"], ["github","linkedin","twitter"]),

    # ── Data ──
    ("#dataanalytics",    "data analytics insights business intelligence reporting",      ["data","tech"], ["linkedin","twitter"]),
    ("#bigdata",          "big data processing Hadoop Spark distributed computing",       ["data","tech"], ["linkedin","twitter","github"]),
    ("#sql",              "SQL database query relational data management PostgreSQL",      ["data","tech"], ["linkedin","github","twitter"]),
    ("#pandas",           "pandas Python data analysis dataframe manipulation CSV",        ["data","code"], ["github","linkedin","twitter"]),
    ("#numpy",            "numpy Python numerical computing arrays matrix math",           ["data","code"], ["github","linkedin","twitter"]),
    ("#powerbi",          "Power BI business intelligence dashboard report visualization",["data","tech"], ["linkedin","twitter"]),
    ("#tableau",          "Tableau data visualization dashboard analytics interactive",   ["data","tech"], ["linkedin","twitter"]),
    ("#dataengineering",  "data engineering pipeline ETL warehouse lakehouse",            ["data","tech"], ["linkedin","twitter","github"]),

    # ── Security ──
    ("#cybersecurity",    "cybersecurity network security hacking protection firewall",   ["security","tech"], ["linkedin","twitter"]),
    ("#ethicalhacking",   "ethical hacking penetration testing security vulnerability",   ["security","tech"], ["linkedin","twitter"]),
    ("#infosec",          "information security data protection privacy compliance",       ["security","tech"], ["linkedin","twitter"]),
    ("#bugbounty",        "bug bounty vulnerability hunting security reward program",     ["security","tech"], ["twitter","linkedin"]),

    # ── Mobile ──
    ("#mobiledev",        "mobile development Android iOS app smartphone cross platform", ["mobile","code"], ["github","linkedin","twitter"]),
    ("#flutter",          "Flutter cross platform mobile app development Dart",           ["mobile","code"], ["github","linkedin","twitter"]),
    ("#android",          "Android mobile app development Java Kotlin Google Play",       ["mobile","code"], ["github","linkedin","twitter"]),
    ("#ios",              "iOS iPhone iPad app development Swift Xcode Apple",            ["mobile","code"], ["github","linkedin","twitter"]),
    ("#reactnative",      "React Native cross platform mobile app JavaScript",            ["mobile","code"], ["github","linkedin","twitter"]),
    ("#kotlin",           "Kotlin Android JVM programming language modern concise",       ["mobile","code"], ["github","linkedin","twitter"]),
    ("#swift",            "Swift iOS macOS Apple programming language safe fast",         ["mobile","code"], ["github","linkedin","twitter"]),

    # ── Business / Career ──
    ("#startup",          "startup entrepreneurship business venture product market fit", ["business"], ["linkedin","twitter","instagram"]),
    ("#entrepreneur",     "entrepreneur business founder startup hustle grind vision",    ["business"], ["linkedin","twitter","instagram"]),
    ("#business",         "business strategy management growth revenue company scale",    ["business"], ["linkedin","twitter","instagram"]),
    ("#marketing",        "marketing digital brand strategy campaign growth viral",       ["business"], ["linkedin","twitter","instagram"]),
    ("#saas",             "SaaS software as a service subscription product B2B",         ["business","tech"], ["linkedin","twitter"]),
    ("#productmanagement","product management roadmap user stories sprint agile",         ["business","tech"], ["linkedin","twitter"]),
    ("#leadership",       "leadership management team motivation strategy vision",        ["business"], ["linkedin","twitter"]),
    ("#productivity",     "productivity workflow efficiency time management GTD",         ["business"], ["linkedin","twitter","instagram"]),
    ("#hiring",           "hiring jobs career opportunity recruitment talent",            ["career"], ["linkedin","twitter"]),
    ("#jobs",             "jobs career opportunity work employment full time",            ["career"], ["linkedin","twitter"]),
    ("#techcareers",      "tech career software engineering jobs growth salary",          ["career","tech"], ["linkedin","twitter"]),
    ("#remotework",       "remote work work from home distributed team async",           ["career"], ["linkedin","twitter","instagram"]),
    ("#btech",            "btech engineering college student degree project India",       ["education"], ["linkedin","twitter","instagram"]),
    ("#cse",              "CSE computer science engineering student project India",       ["education","tech"], ["linkedin","twitter","instagram"]),
    ("#collegelife",      "college life student campus study friends hostel India",      ["education"], ["instagram","twitter"]),
    ("#finalyear",        "final year project btech engineering college capstone",        ["education","tech"], ["linkedin","twitter","instagram"]),
    ("#placementprep",    "placement preparation interview coding DSA jobs campus",      ["education","career"], ["linkedin","twitter"]),
    ("#campuslife",       "campus life college student university India hostel fun",     ["education"], ["instagram","twitter"]),

    # ── Fitness ──
    ("#fitness",          "fitness workout exercise gym training health body strength",   ["fitness"], ["instagram","twitter","youtube"]),
    ("#workout",          "workout training exercise gym fitness routine sets reps",      ["fitness"], ["instagram","twitter","youtube"]),
    ("#gym",              "gym workout training bodybuilding strength muscle gains",      ["fitness"], ["instagram","twitter","youtube"]),
    ("#nutrition",        "nutrition diet food health wellness meal prep macros",         ["fitness","food"], ["instagram","twitter"]),
    ("#yoga",             "yoga meditation mindfulness flexibility balance poses",        ["fitness","wellness"], ["instagram","twitter","youtube"]),
    ("#healthylifestyle", "healthy lifestyle wellness diet exercise balance self care",  ["fitness"], ["instagram","twitter","youtube"]),
    ("#weightloss",       "weight loss diet exercise fitness transformation journey",     ["fitness"], ["instagram","youtube"]),
    ("#running",          "running marathon jogging cardio fitness outdoor road trail",  ["fitness","outdoor"], ["instagram","twitter","youtube"]),
    ("#legday",           "leg day gym workout squat lunge deadlift fitness training",   ["fitness"], ["instagram","twitter","youtube"]),
    ("#morningworkout",   "morning workout exercise gym routine fitness energy health",  ["fitness"], ["instagram","twitter","youtube"]),
    ("#fitlife",          "fit life fitness healthy lifestyle active workout motivation", ["fitness"], ["instagram","twitter","youtube"]),
    ("#strengthtraining", "strength training gym weights muscle build powerlifting",     ["fitness"], ["instagram","twitter","youtube"]),
    ("#cycling",          "cycling bike outdoor fitness cardio road mountain sport",     ["fitness","outdoor"], ["instagram","twitter","youtube"]),
    ("#swimming",         "swimming pool open water fitness cardio sport aquatic",       ["fitness"], ["instagram","twitter","youtube"]),

    # ── Food ──
    ("#food",             "food recipe cooking eating delicious meal dinner lunch",      ["food"], ["instagram","youtube","twitter"]),
    ("#foodie",           "foodie gourmet restaurant review dining eat explore taste",   ["food"], ["instagram","youtube","twitter"]),
    ("#cooking",          "cooking recipe kitchen homemade food preparation technique",  ["food"], ["instagram","youtube","twitter"]),
    ("#recipe",           "recipe ingredients cooking instructions food make step",      ["food"], ["instagram","youtube","twitter"]),
    ("#healthyfood",      "healthy food nutrition clean eating organic whole natural",   ["food","fitness"], ["instagram","youtube"]),
    ("#vegan",            "vegan plant based diet no meat dairy ethical lifestyle",      ["food"], ["instagram","youtube","twitter"]),
    ("#baking",           "baking bread cake pastry oven dessert sweet flour butter",   ["food"], ["instagram","youtube","twitter"]),
    ("#mealprep",         "meal prep cooking batch healthy food preparation weekly",    ["food","fitness"], ["instagram","youtube","twitter"]),
    ("#homemade",         "homemade food cooking recipe kitchen fresh made love",        ["food"], ["instagram","youtube","twitter"]),
    ("#streetfood",       "street food local eat culture taste explore city market",    ["food","travel"], ["instagram","youtube","twitter"]),
    ("#indianfood",       "Indian food curry spice recipe cook biryani chai desi",      ["food"], ["instagram","youtube","twitter"]),
    ("#coffee",           "coffee cafe morning brew espresso latte cappuccino",          ["food"], ["instagram","twitter","youtube"]),

    # ── Travel ──
    ("#travel",           "travel journey adventure explore destination trip vacation",  ["travel"], ["instagram","youtube","twitter"]),
    ("#wanderlust",       "wanderlust travel adventure explore world journey discover",  ["travel"], ["instagram","youtube","twitter"]),
    ("#photography",      "photography photo camera capture landscape portrait art",     ["photo"], ["instagram","twitter","youtube"]),
    ("#travelphotography","travel photography landscape destination journey explore",    ["travel","photo"], ["instagram","twitter"]),
    ("#backpacking",      "backpacking solo travel budget adventure hostel explore",     ["travel"], ["instagram","youtube","twitter"]),
    ("#digitalnomad",     "digital nomad remote work travel laptop lifestyle freedom",  ["travel","career"], ["instagram","twitter","linkedin"]),
    ("#incredibleindia",  "incredible India travel culture heritage temple nature",      ["travel"], ["instagram","twitter","youtube"]),
    ("#solotravel",       "solo travel adventure independent explore freedom discover",  ["travel"], ["instagram","twitter","youtube"]),
    ("#travelgram",       "travel gram photography explore destination adventure trip",  ["travel","photo"], ["instagram","twitter"]),
    ("#roadtrip",         "road trip drive explore destination adventure highway",       ["travel"], ["instagram","twitter","youtube"]),

    # ── Motivation ──
    ("#motivation",       "motivation inspiration success mindset goals achievement",    ["motivation"], ["instagram","twitter","linkedin","youtube"]),
    ("#inspiration",      "inspiration creative ideas motivational quotes positive",     ["motivation"], ["instagram","twitter","linkedin"]),
    ("#mindset",          "mindset growth positive thinking success habits mental",      ["motivation"], ["instagram","twitter","linkedin"]),
    ("#success",          "success achievement goals hard work results win hustle",      ["motivation"], ["instagram","twitter","linkedin"]),
    ("#growthmindset",    "growth mindset learning improvement development evolve",      ["motivation"], ["instagram","twitter","linkedin"]),
    ("#personaldevelopment","personal development self improvement habits goals life",  ["motivation"], ["instagram","twitter","linkedin"]),
    ("#dailymotivation",  "daily motivation morning quotes inspiration positive energy", ["motivation"], ["instagram","twitter"]),
    ("#selfimprovement",  "self improvement habits routine discipline growth better",   ["motivation"], ["instagram","twitter","linkedin"]),
    ("#hustle",           "hustle grind work hard entrepreneur success ambition goal",  ["motivation","business"], ["instagram","twitter","linkedin"]),

    # ── Education ──
    ("#education",        "education learning school university knowledge skill teach",  ["education"], ["linkedin","twitter","youtube"]),
    ("#elearning",        "e-learning online course education digital platform",         ["education"], ["linkedin","twitter","youtube"]),
    ("#edtech",           "education technology learning platform online digital",       ["education","tech"], ["linkedin","twitter"]),
    ("#student",          "student college university degree learning study exam prep",  ["education"], ["twitter","instagram","linkedin"]),
    ("#onlinelearning",   "online learning course tutorial self-paced certificate",      ["education"], ["linkedin","twitter","youtube"]),
    ("#studygram",        "study gram notes books learning student academic exam",       ["education"], ["instagram","twitter"]),
    ("#learnpython",      "learn Python programming beginner tutorial code project",    ["education","code"], ["github","twitter","linkedin"]),
    ("#coding101",        "coding beginner tutorial learn programming basics start",    ["education","code"], ["twitter","instagram","youtube"]),

    # ── Finance ──
    ("#investing",        "investing stocks bonds portfolio wealth building returns",    ["finance"], ["twitter","linkedin","youtube"]),
    ("#personalfinance",  "personal finance money management budget savings expense",   ["finance"], ["twitter","linkedin","youtube"]),
    ("#crypto",           "cryptocurrency Bitcoin Ethereum blockchain DeFi Web3",       ["finance"], ["twitter","linkedin"]),
    ("#stockmarket",      "stock market trading shares investment portfolio Nifty",     ["finance"], ["twitter","linkedin","youtube"]),
    ("#financialfreedom", "financial freedom passive income wealth retire early FIRE",  ["finance"], ["twitter","linkedin","instagram"]),
    ("#nifty50",          "Nifty 50 stock market India NSE BSE trading investment",    ["finance"], ["twitter","linkedin"]),
    ("#mutualfunds",      "mutual funds SIP investment returns India SEBI finance",    ["finance"], ["twitter","linkedin"]),

    # ── Gaming ──
    ("#gaming",           "gaming video games console PC stream play online",           ["gaming"], ["youtube","twitter","instagram"]),
    ("#gamer",            "gamer gaming community stream play esports online",          ["gaming"], ["youtube","twitter","instagram"]),
    ("#esports",          "esports competitive gaming tournament team prize",           ["gaming"], ["youtube","twitter","instagram"]),
    ("#gamedev",          "game development Unity Unreal design indie studio",          ["gaming","code"], ["github","twitter","youtube"]),
    ("#mobilegaming",     "mobile gaming smartphone app play online casual",            ["gaming"], ["youtube","twitter","instagram"]),

    # ── Art / Design ──
    ("#art",              "art drawing painting creative illustration design visual",   ["art"], ["instagram","twitter","youtube"]),
    ("#design",           "design UI UX graphic visual creative branding identity",     ["art","tech"], ["instagram","linkedin","twitter"]),
    ("#uidesign",         "UI design interface user experience product digital",         ["art","tech"], ["instagram","linkedin","twitter"]),
    ("#graphicdesign",    "graphic design visual branding logo creative typography",    ["art"], ["instagram","linkedin","twitter"]),
    ("#digitalart",       "digital art illustration creative Procreate drawing",        ["art"], ["instagram","twitter","youtube"]),
    ("#sketching",        "sketching drawing art pencil illustration creative",         ["art"], ["instagram","twitter","youtube"]),

    # ── Nature / Environment ──
    ("#nature",           "nature environment landscape wildlife outdoor green",         ["nature"], ["instagram","twitter","youtube"]),
    ("#sustainability",   "sustainability environment green eco climate conscious",      ["nature"], ["instagram","twitter","linkedin"]),
    ("#climatechange",    "climate change environment global warming action protest",    ["nature"], ["twitter","linkedin","instagram"]),
    ("#wildlife",         "wildlife animals nature conservation outdoor safari",         ["nature"], ["instagram","twitter","youtube"]),
    ("#earthday",         "earth day environment nature green clean planet save",        ["nature"], ["instagram","twitter","linkedin"]),
    ("#gogreen",          "go green environment sustainable eco friendly nature",        ["nature"], ["instagram","twitter","linkedin"]),

    # ── Mental Health / Wellness ──
    ("#mentalhealth",     "mental health wellbeing anxiety stress therapy self care",   ["wellness"], ["instagram","twitter","linkedin"]),
    ("#selfcare",         "self care routine wellness mental health relax recharge",    ["wellness"], ["instagram","twitter"]),
    ("#meditation",       "meditation mindfulness peace calm breath stress relief",     ["wellness","fitness"], ["instagram","twitter","youtube"]),
    ("#wellness",         "wellness health holistic balance mind body soul lifestyle",  ["wellness"], ["instagram","twitter","youtube"]),
    ("#mindfulness",      "mindfulness present moment awareness calm peace mental",     ["wellness"], ["instagram","twitter","youtube"]),

    # ── Photography ──
    ("#photooftheday",    "photo of the day photography capture moment beautiful",      ["photo"], ["instagram","twitter"]),
    ("#portraitphotography","portrait photography face person light studio outdoor",    ["photo"], ["instagram","twitter"]),
    ("#streetphotography","street photography city urban candid documentary life",      ["photo"], ["instagram","twitter"]),
    ("#astrophotography", "astrophotography stars galaxy milky way night sky",          ["photo","outdoor"], ["instagram","twitter","youtube"]),
    ("#mobilephotography","mobile photography smartphone camera shot edit",             ["photo"], ["instagram","twitter"]),
    ("#lightroom",        "Lightroom photo editing presets color grade photography",    ["photo"], ["instagram","twitter","youtube"]),

    # ── Trending / Viral ──
    ("#trending",         "trending viral popular social media content current",        ["trending"], ["instagram","twitter","youtube","linkedin"]),
    ("#viral",            "viral trending popular share engage content social media",   ["trending"], ["instagram","twitter","youtube"]),
    ("#reels",            "reels short video Instagram content creator viral",          ["trending"], ["instagram","youtube"]),
    ("#shorts",           "shorts YouTube short video content creator viral trending",  ["trending"], ["youtube","instagram"]),
    ("#contentcreator",   "content creator social media video photo post engage",       ["trending"], ["instagram","youtube","twitter","linkedin"]),
    ("#influencer",       "influencer social media brand collaboration audience reach", ["trending"], ["instagram","youtube","twitter"]),

    # ── India Specific ──
    ("#india",            "India culture diversity tradition food travel people desi",  ["india"], ["instagram","twitter","youtube"]),
    ("#indian",           "Indian culture tradition food festival diversity heritage",  ["india"], ["instagram","twitter","youtube"]),
    ("#desi",             "desi Indian culture food lifestyle tradition relatable",     ["india"], ["instagram","twitter","youtube"]),
    ("#indianstartup",    "Indian startup ecosystem founder tech product Bangalore",   ["india","business"], ["linkedin","twitter"]),
    ("#makeinindia",      "Make in India startup manufacturing tech product local",    ["india","business"], ["linkedin","twitter"]),
    ("#iit",              "IIT engineering technology institute India premier college", ["india","education"], ["linkedin","twitter","instagram"]),
    ("#nit",              "NIT engineering college India technology degree project",   ["india","education"], ["linkedin","twitter","instagram"]),
]


POPULARITY = {
    # Outdoor
    "#hiking":89,"#trekking":85,"#mountains":87,"#outdoors":83,
    "#adventure":88,"#camping":82,"#naturephotography":80,
    "#mountaineering":72,"#hikingadventure":76,"#trailrunning":74,
    "#mountainlife":71,"#exploreoutdoors":75,"#wilderness":73,
    "#summit":70,"#backpacker":72,"#landscape":84,"#forest":80,
    "#sunset":92,"#sunrise":88,"#oceanview":82,"#cycling":78,"#swimming":72,
    # AI/ML
    "#artificialintelligence":89,"#machinelearning":83,"#deeplearning":82,
    "#datascience":81,"#neuralnetworks":75,"#generativeai":85,"#llm":80,
    "#promptengineering":70,"#mlops":62,"#nlp":74,"#computervision":72,
    "#chatgpt":88,"#aitools":76,"#tensorflow":76,"#pytorch":77,
    # Code
    "#python":80,"#javascript":79,"#typescript":75,"#reactjs":74,
    "#nodejs":73,"#django":68,"#flask":66,"#fastapi":67,"#golang":70,
    "#rust":68,"#java":72,"#cpp":65,"#coding":82,"#programming":81,
    "#developer":79,"#100daysofcode":65,"#opensource":76,
    "#buildinpublic":72,"#sideproject":68,"#indiehacker":70,
    # Web
    "#webdev":78,"#webdevelopment":77,"#frontend":71,"#backend":70,
    "#fullstack":73,"#html":68,"#css":70,"#api":68,"#restapi":67,"#graphql":65,
    # DevOps
    "#devops":71,"#docker":72,"#kubernetes":65,"#aws":74,"#azure":71,
    "#gcp":69,"#cloudcomputing":74,"#cicd":64,"#terraform":59,"#githubactions":62,
    # Data
    "#dataanalytics":73,"#bigdata":72,"#sql":67,"#pandas":70,"#numpy":68,
    "#powerbi":68,"#tableau":67,"#dataengineering":70,
    # Security
    "#cybersecurity":72,"#ethicalhacking":65,"#infosec":68,"#bugbounty":58,
    # Mobile
    "#mobiledev":70,"#flutter":70,"#android":72,"#ios":71,"#reactnative":69,
    "#kotlin":68,"#swift":67,"#mobilegaming":75,
    # Business
    "#startup":77,"#entrepreneur":75,"#business":87,"#marketing":80,
    "#saas":72,"#productmanagement":70,"#leadership":74,"#productivity":73,
    "#hiring":72,"#jobs":74,"#techcareers":70,"#remotework":71,
    "#hustle":76,"#indianstartup":68,"#makeinindia":65,
    # Education
    "#education":78,"#elearning":72,"#edtech":68,"#student":74,
    "#onlinelearning":70,"#btech":65,"#cse":62,"#collegelife":68,
    "#finalyear":60,"#placementprep":63,"#campuslife":66,"#studygram":70,
    "#learnpython":63,"#coding101":60,"#iit":70,"#nit":65,
    # Fitness
    "#fitness":90,"#workout":85,"#gym":84,"#nutrition":78,"#yoga":80,
    "#healthylifestyle":82,"#weightloss":79,"#running":76,
    "#legday":78,"#morningworkout":75,"#fitlife":77,"#strengthtraining":74,
    # Food
    "#food":91,"#foodie":85,"#cooking":82,"#recipe":80,"#healthyfood":76,
    "#vegan":74,"#baking":72,"#mealprep":76,"#homemade":73,
    "#streetfood":75,"#indianfood":78,"#coffee":84,
    # Travel
    "#travel":92,"#wanderlust":88,"#photography":93,"#travelphotography":80,
    "#backpacking":72,"#digitalnomad":70,"#incredibleindia":75,
    "#solotravel":74,"#travelgram":76,"#roadtrip":78,
    # Motivation
    "#motivation":88,"#inspiration":86,"#mindset":82,"#success":85,
    "#growthmindset":78,"#personaldevelopment":76,"#dailymotivation":74,
    "#selfimprovement":76,"#hustle":76,
    # Finance
    "#investing":75,"#personalfinance":74,"#crypto":80,"#stockmarket":76,
    "#financialfreedom":72,"#nifty50":68,"#mutualfunds":70,
    # Gaming
    "#gaming":84,"#gamer":80,"#esports":78,"#gamedev":65,
    # Art
    "#art":90,"#design":80,"#uidesign":72,"#graphicdesign":74,"#digitalart":76,
    "#sketching":70,"#lightroom":72,
    # Nature
    "#nature":89,"#sustainability":75,"#climatechange":74,"#wildlife":72,
    "#earthday":70,"#gogreen":72,
    # Wellness
    "#mentalhealth":82,"#selfcare":80,"#meditation":82,
    "#wellness":80,"#mindfulness":78,
    # Photo
    "#photooftheday":90,"#portraitphotography":78,"#streetphotography":75,
    "#astrophotography":70,"#mobilephotography":72,
    # Trending
    "#trending":96,"#viral":95,"#reels":82,"#shorts":80,
    "#contentcreator":78,"#influencer":76,
    # India
    "#india":85,"#indian":82,"#desi":78,
    
    "#iceland":82,"#europe":85,"#northernlights":88,"#scandinavia":75,
    "#norway":80,"#switzerland":82,"#bali":90,"#thailand":88,
    "#paris":87,"#japan":89,"#maldives":85,"#goa":82,
    "#kerala":78,"#rajasthan":80,"#himalayas":83,"#leh":76,
    "#snow":85,"#winter":82,"#summer":88,"#monsoon":72,
    "#skiing":78,"#scubadiving":74,"#surfing":80,
    "#paragliding":72,"#skydiving":70,
}


class MLHashtagEngine:
    def __init__(self):
        self.model          = None
        self.kw_model       = None
        self.tag_embeddings = None
        self.tags           = []
        self.descriptions   = []
        self.categories     = []
        self.platforms      = []
        self.ready          = False
        self._load_models()

    def _load_models(self):
        if not SENTENCE_TRANSFORMERS_OK:
            print("[ml_engine] Running in TF-IDF fallback mode")
            self._setup_data()
            return
        try:
            print("[ml_engine] Loading sentence-transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[ml_engine] Model loaded!")
            if KEYBERT_OK:
                self.kw_model = KeyBERT(model=self.model)
                print("[ml_engine] KeyBERT ready!")
            self._setup_data()
            print("[ml_engine] Computing hashtag embeddings...")
            self.tag_embeddings = self.model.encode(
                self.descriptions,
                show_progress_bar=False,
                batch_size=64,
                normalize_embeddings=True
            )
            self.ready = True
            print(f"[ml_engine] Ready! {len(self.tags)} hashtags indexed.")
        except Exception as e:
            print(f"[ml_engine] Model load failed: {e}")
            self._setup_data()
            self.ready = False

    def _setup_data(self):
        self.tags         = [row[0] for row in HASHTAG_DB]
        self.descriptions = [row[1] for row in HASHTAG_DB]
        self.categories   = [row[2] for row in HASHTAG_DB]
        self.platforms    = [row[3] for row in HASHTAG_DB]

    def _tfidf_fallback(self, text, platform='all', count=20):
        if not SKLEARN_OK or not self.tags:
            return []
        try:
            corpus      = [text] + self.descriptions
            vectorizer  = TfidfVectorizer(ngram_range=(1,2), stop_words='english', max_features=5000)
            tfidf_matrix = vectorizer.fit_transform(corpus)
            user_vec     = tfidf_matrix[0]
            hashtag_vecs = tfidf_matrix[1:]
            similarities = sk_cosine(user_vec, hashtag_vecs)[0]
            top_indices  = np.argsort(similarities)[::-1][:count*2]
            results = []
            for idx in top_indices:
                if similarities[idx] < 0.01:
                    continue
                tag      = self.tags[idx]
                sim      = float(similarities[idx])
                pop      = POPULARITY.get(tag, 50)
                combined = sim * 0.6 + (pop / 100) * 0.4
                results.append({'tag':tag,'score':pop,'similarity':round(sim,4),'combined':round(combined,4),'method':'tfidf'})
            results.sort(key=lambda x: x['combined'], reverse=True)
            return results[:count]
        except Exception as e:
            print(f"[ml_engine] TF-IDF failed: {e}")
            return []

    def extract_keywords(self, text, top_n=8):
        if self.kw_model and KEYBERT_OK:
            try:
                keywords = self.kw_model.extract_keywords(
                    text, keyphrase_ngram_range=(1,2),
                    stop_words='english', use_mmr=True,
                    diversity=0.5, top_n=top_n
                )
                return [kw for kw, _ in keywords]
            except Exception as e:
                print(f"[ml_engine] KeyBERT failed: {e}")
        words    = re.sub(r'[^a-z\s]', ' ', text.lower()).split()
        stopwords = {'the','a','an','and','or','but','in','on','at','to','for',
                     'of','with','by','from','is','are','was','were','be','been',
                     'have','has','do','does','will','would','could','should',
                     'this','that','i','me','my','we','you','he','she','it','they'}
        freq = Counter(w for w in words if w not in stopwords and len(w) > 3)
        return [w for w, _ in freq.most_common(top_n)]

    def generate(self, text, platform='all', count=20):
        if not text or len(text.strip()) < 3:
            return []
        keywords = self.extract_keywords(text, top_n=8)
        print(f"[ml_engine] Keywords: {keywords}")

        if not self.ready or self.tag_embeddings is None:
            return self._format_results(self._tfidf_fallback(text, platform, count))

        try:
            text_embedding = self.model.encode(
                text, normalize_embeddings=True, show_progress_bar=False
            )
            similarities = np.dot(self.tag_embeddings, text_embedding)
            raw = []
            for i, sim in enumerate(similarities):
                tag   = self.tags[i]
                plats = self.platforms[i]
                pop   = POPULARITY.get(tag, 50)
                if platform != 'all' and platform not in plats:
                    continue
                platform_bonus = 0.05 if platform in plats else 0
                combined = (float(sim)*0.75) + ((pop/100)*0.20) + platform_bonus
                raw.append({'tag':tag,'score':pop,'similarity':round(float(sim),4),'combined':round(combined,4),'method':'sentence_transformer'})

            raw.sort(key=lambda x: x['combined'], reverse=True)
            seen, final = set(), []
            for r in raw:
                if r['tag'] not in seen:
                    seen.add(r['tag'])
                    final.append(r)
                if len(final) >= count:
                    break

            print(f"[ml_engine] Generated {len(final)} semantic hashtags")
            return self._format_results(final)
        except Exception as e:
            print(f"[ml_engine] Semantic search failed: {e}")
            return self._format_results(self._tfidf_fallback(text, platform, count))

    def _get_category(self, score):
        if score >= 75: return 'trending'
        if score >= 55: return 'broad'
        return 'niche'

    def _format_results(self, results):
        from src.nlp import get_score_label
        formatted = []
        for r in results:
            score = r.get('score', 50)
            formatted.append({
                'tag':        r['tag'],
                'score':      score,
                'label':      get_score_label(score),
                'category':   self._get_category(score),
                'similarity': r.get('similarity', 0),
                'source':     'ml_semantic',
                'method':     r.get('method', 'sentence_transformer'),
            })
        return formatted


_engine = None

def get_engine():
    global _engine
    if _engine is None:
        print("[ml_engine] Initializing ML engine...")
        _engine = MLHashtagEngine()
    return _engine