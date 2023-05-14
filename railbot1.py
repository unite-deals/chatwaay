import streamlit as st
import openai
import requests
from requests.exceptions import HTTPError
import geopy
import geopy.distance
import json
import urllib.request
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import requests
#from streamlit_webrtc import VideoTransformerBase, webrtc_streamer
#from streamlit.report_thread import get_report_ctx
#from streamlit.server.server import Server
# Set up OpenAI API


def get_gmaps_html(lat, lon):
    gmaps_html = f"""
        <iframe
            width="600"
            height="450"
            frameborder="0" style="border:0"
            src="https://www.google.com/maps/embed/v1/place?key=API_KEY&q={lat},{lon}&zoom=15"
            allowfullscreen>
        </iframe>
    """
    return gmaps_html
# Define Streamlit app
def get_location(ip_address):
    # use ipstack api to get location data
    url = f"http://api.ipstack.com/{ip_address}?access_key=<your_access_key>"
    response = requests.get(url)
    location_data = response.json()
    return location_data

def get_ip_address():
    # get remote IP address
    ip_address = None
    try:
        url = 'https://jsonip.com/'
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        ip_address = data['ip']
        print(ip_address)
    except:
        pass
    if ip_address is None:
        ip_address = '127.0.0.1' # default to localhost
    return ip_address



# get remote IP address
#

# get location data for the IP address
#location_data = get_location(ip_address)

def app():
    # Set page title and icon
    st.set_page_config(page_title="Indian Railway Chatbot", page_icon=":train:")

    # Set up chat interface
    st.markdown("""
        <style>
            .chat-box {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 10px;
            }
            .user-message {
                margin-bottom: 10px;
            }
            .bot-message {
                margin-top: 10px;
            }
            .message-icon {
                font-size: 1.5rem;
                margin-right: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Define chat function
    def chat(user_input):
        # Send user message to OpenAI API
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"""reply in extra careing soft tone with some friendly supporting , 
                try solve the problem intelligently , guiding the purposes of journey , 
                helping in modds , cheering , motivativating , roamancing , message 
                like more than a normal helping assistant from indian railway services  but also extra care with support & other supporting assistant to te user like advice for health 
                food habits , suggestion and guidance for travel purposes , if business , helping in creating presentation , cover letter etc..
                if for medical give some motivational and yoga tips , pro level asking , suggestion , helps. User can feels as a personal assistant .  :{user_input}.""",
                max_tokens=200,
                n=1,
                temperature=0.7,
                frequency_penalty=0.5,
                presence_penalty=0.5,
                stop=['<<END>>'],
            )
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return

        # Check if OpenAI response is empty
        if not response.choices:
            st.warning("No response received from OpenAI.")
            return

        # Display OpenAI response in chat interface
        bot_message = response.choices[0].text
        if bot_message:
            st.markdown("""
                <div class="chat-box bot-message">
                    <span class="message-icon">:train:</span>
                    {0}
                </div>
            """.format(bot_message), unsafe_allow_html=True)

    # Display welcome message
    st.title("Welcome to the Indian Railway Chatbot!")
    st.markdown("I can help you with train booking, services ,checking, and other supporting assitance. You can also pass the time by chatting with me or getting travel recommendations.")

    # Set up chat form
    user_input = st.text_input("Enter your message")

    # Set up send button
    if st.button("Send"):
        chat(user_input)
    # Set up menu options
    st.sidebar.title("Menu")
    #ip_address = st.request.remote_ip
    # Train booking
    if st.sidebar.button("Train Booking"):
        st.header("Train Booking")
        st.subheader("Enter your details")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        from_place = st.text_input("From")
        to_place = st.text_input("To")
        date = st.date_input("Date")
        class_type = st.selectbox("Class", ["Sleeper", "AC 3 Tier", "AC 2 Tier"])
        st.write("You have entered:")
        st.write(f"Name: {name}")
        st.write(f"Age: {age}")
        st.write(f"From: {from_place}")
        st.write(f"To: {to_place}")
        st.write(f"Date: {date}")
        st.write(f"Class: {class_type}")
        st.markdown("You selected Train Booking. Please visit the Indian Railways website to book your train tickets: https://www.irctc.co.in/nget/train-search")

    # Auto geolocation to show maps for nearest police stations
    # get remote IP address
    ip_address = get_ip_address()

    # get location data for the IP address
    location_data = get_location(ip_address)
    if st.sidebar.button("Nearest Police Stations"):
        # Get user location using IP address
        
        # Get user coordinates using GeoIP database
        try:
            geolocator = geopy.geocoders.Nominatim(user_agent="Idian Railway Chatbot")
            location = geolocator.geocode(ip_address , timeout=1000)
            user_latitude = location.latitude
            user_longitude = location.longitude
        except geopy.exc.GeocoderTimedOut:
            st.warning("Location data not found.")
            return

        # Display user location
        st.markdown(f"Your current location is: ({user_latitude:.6f}, {user_longitude:.6f})")
        response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"What is the nearest police station to {user_latitude},{user_longitude}?",
        max_tokens=1024,
        temperature=0.7,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=['<<END>>'],
        )

        # Display the response
        st.write("Nearest police station:", response.choices[0].text)
        #else:
            #st.write("Could not get your location")
        # Query OpenStreetMap Overpass API to get nearest police station
        st.write("Here's a map of your current location:")
        gmaps_html = get_gmaps_html(user_latitude, user_longitude)
        components.html(gmaps_html, height=500)
        overpass_url = f"https://overpass-api.de/api/interpreter?data=[out:json];node(around:5000,{user_latitude},{user_longitude})[\"amenity\"=\"police\"];out;"
        overpass_response = requests.get(overpass_url)
        overpass_data = overpass_response.json()

        # Get nearest police station name and coordinates
        try:
            police_station = overpass_data["elements"][0]["tags"]["name"]
            police_station_latitude = overpass_data["elements"][0]["lat"]
            police_station_longitude = overpass_data["elements"][0]["lon"]
        except IndexError:
            st.warning("No police station found within 5km.")
            return

        # Display nearest police station
        st.markdown(f"The nearest police station is: {police_station} ({police_station_latitude:.6f}, {police_station_longitude:.6f})")
    # Medical support
    if st.sidebar.button("Medical Support"):
        st.markdown("You selected Medical Support. Please call the Indian Railways helpline at 138 for medical assistance during your train journey.")

    # Travel recommendations
    if st.sidebar.button("Travel Recommendations"):
        st.markdown("You selected Travel Recommendations. Here are some popular travel destinations in India:")
        st.markdown("Upcoming railway tour packages are coming")
        st.write("- Taj Mahal in Agra, Uttar Pradesh")
        st.write("- Hawa Mahal in Jaipur, Rajasthan")
        st.write("- Golden Temple in Amritsar, Punjab")
        st.write("- Charminar in Hyderabad, Telangana")
        st.write("- Gateway of India in Mumbai, Maharashtra")
        st.header("Travel Destinations")
        st.subheader("Here are some popular travel destinations in India")
        st.write("- Goa")
        st.write("- Jaipur")
        st.write("- Shimla")
        st.write("- Darjeeling")
        st.write("- Agra")
        st.write("- Munnar")
        st.write("- Ooty")
        st.write("- Kerala")
        st.write("- Leh Ladakh")
        st.write("- Andaman and Nicobar Islands")
        st.write("- Varanasi")
        st.write("- Rishikesh")
    if st.sidebar.button("Camera Features "):
        st.markdown("You selected Travel photography to display for IRCTC Stock phtography contest . Complaint features  ")

        if st.button('Open Camera'):
            webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)
        submit = st.button("Submit")

        if submit:
            st.write("Complaint submitted!")
    if st.sidebar.button("Camera Features for help"):
        st.markdown("You can share any incedents happnening in train . Complaint features , your information will hide ,   ")
        if st.button('Open Camera'):
            webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)
        # Complaints form
        st.write("## Complaints Form")

        name = st.text_input("Name")
        complaint = st.text_area("Complaint")
        submit = st.button("Submit")

        if submit:
            st.write("Complaint submitted!")
# Run Streamlit app
if __name__ == "__main__":
    app()
