from datetime import date

from flyingfox_app.models import (
    Ride,
    RidePrice,
)

from .languages import get_language
from .intents import detect_intent
from .entities import find_ride
from .responses import get_response
from .context import (
    get_context,
    update_context,
)


# =========================================================
# CURRENT RIDE PRICE
# =========================================================

def get_current_ride_price(ride):

    today = date.today()

    return (
        RidePrice.objects
        .filter(
            ride=ride,
            ride__is_active=True,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by(
            "-start_date",
            "-created_at",
        )
        .first()
    )


# =========================================================
# MAIN CHATBOT ENGINE
# =========================================================

def process_message(
    chat_session,
    user_message,
):

    language = get_language(
        chat_session.language
    )

    context = get_context(
        chat_session
    )

    # =====================================================
    # 1. DETECT INTENT
    # =====================================================

    intent, confidence = detect_intent(
        user_message,
        language,
    )

    # =====================================================
    # 2. DETECT RIDE
    # =====================================================

    detected_ride = find_ride(
        user_message
    )

    ride = detected_ride

    if detected_ride:

        update_context(
            chat_session,
            selected_ride_id=detected_ride.id,
        )

    else:

        selected_ride_id = context.get(
            "selected_ride_id"
        )

        if selected_ride_id:

            ride = (
                Ride.objects
                .filter(
                    id=selected_ride_id,
                    is_active=True,
                )
                .first()
            )

    # =====================================================
    # 3. HANDLE RIDE SELECTION FOLLOW-UP
    # =====================================================

    awaiting = context.get("awaiting")
    last_intent = context.get("last_intent")

    if (
        detected_ride
        and awaiting == "ride_selection"
    ):

        if last_intent == "ride_price":
            intent = "ride_price"

        elif last_intent == "ride_list":

            # User selected a ride after viewing ride list.
            # Give a simple ride-specific response.

            if language == "ml":

                response = (
                    f"നിങ്ങൾ {detected_ride.name} തിരഞ്ഞെടുത്തു 😊\n\n"
                    "ഈ റൈഡിന്റെ വില അറിയണോ, അല്ലെങ്കിൽ ബുക്ക് ചെയ്യണോ?"
                )

            elif language == "hi":

                response = (
                    f"आपने {detected_ride.name} चुना है 😊\n\n"
                    "क्या आप इसकी कीमत जानना चाहते हैं या इसे बुक करना चाहते हैं?"
                )

            elif language == "ta":

                response = (
                    f"நீங்கள் {detected_ride.name} ரைடை தேர்வு செய்துள்ளீர்கள் 😊\n\n"
                    "இதன் விலையை தெரிந்துகொள்ள வேண்டுமா அல்லது புக் செய்ய வேண்டுமா?"
                )

            else:

                response = (
                    f"You selected {detected_ride.name} 😊\n\n"
                    "Would you like to know the price or book this ride?"
                )

            update_context(
                chat_session,
                last_intent="ride_selected",
                selected_ride_id=detected_ride.id,
                awaiting="ride_action",
            )

            return {
                "response": response,
                "intent": "ride_selected",
                "response_type": "text",
                "show_quick_replies": True,
            }

    # =====================================================
    # 4. GREETING
    # =====================================================

    if intent == "greeting":

        response = get_response(
            "greeting",
            language,
            name=(
                chat_session.customer_name
                or ""
            ),
        )

        update_context(
            chat_session,
            last_intent="greeting",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "greeting",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 5. RIDE PRICE
    # =====================================================

    if intent == "ride_price":

        # -------------------------------------------------
        # Specific ride price
        # -------------------------------------------------

        if ride:

            price = get_current_ride_price(
                ride
            )

            if price:

                if language == "ml":

                    response = (
                        f"{ride.name} റൈഡിന്റെ നിലവിലെ "
                        f"നിരക്ക് ഒരാൾക്ക് ₹{price.price:,.2f} ആണ് 😊\n\n"
                        "ഈ റൈഡ് ബുക്ക് ചെയ്യാൻ താൽപര്യമുണ്ടോ?"
                    )

                elif language == "hi":

                    response = (
                        f"{ride.name} की मौजूदा कीमत "
                        f"₹{price.price:,.2f} प्रति व्यक्ति है 😊\n\n"
                        "क्या आप इस राइड को बुक करना चाहेंगे?"
                    )

                elif language == "ta":

                    response = (
                        f"{ride.name} ரைடின் தற்போதைய கட்டணம் "
                        f"ஒருவருக்கு ₹{price.price:,.2f} 😊\n\n"
                        "இந்த ரைடை புக் செய்ய விரும்புகிறீர்களா?"
                    )

                else:

                    response = (
                        f"{ride.name} currently costs "
                        f"₹{price.price:,.2f} per rider 😊\n\n"
                        "Would you like to book this ride?"
                    )

                update_context(
                    chat_session,
                    last_intent="ride_price",
                    selected_ride_id=ride.id,
                    awaiting="booking_confirmation",
                )

                return {
                    "response": response,
                    "intent": "ride_price",
                    "response_type": "text",
                    "show_quick_replies": True,
                }

        # -------------------------------------------------
        # Show all current prices
        # -------------------------------------------------

        prices = (
            RidePrice.objects
            .filter(
                ride__is_active=True,
                is_active=True,
                start_date__lte=date.today(),
                end_date__gte=date.today(),
            )
            .select_related("ride")
            .order_by(
                "ride__name",
                "-start_date",
            )
        )

        seen = set()
        lines = []

        for price in prices:

            if price.ride_id in seen:
                continue

            seen.add(
                price.ride_id
            )

            lines.append(
                f"• {price.ride.name} — "
                f"₹{price.price:,.2f}"
            )

        if lines:

            if language == "ml":

                heading = (
                    "ഇപ്പോഴത്തെ റൈഡ് നിരക്കുകൾ:"
                )

                footer = (
                    "\n\nഏത് റൈഡിനെ കുറിച്ചാണ് "
                    "കൂടുതൽ അറിയേണ്ടത്?"
                )

            elif language == "hi":

                heading = (
                    "मौजूदा राइड की कीमतें:"
                )

                footer = (
                    "\n\nआप किस राइड के बारे में "
                    "अधिक जानना चाहते हैं?"
                )

            elif language == "ta":

                heading = (
                    "தற்போதைய ரைடு கட்டணங்கள்:"
                )

                footer = (
                    "\n\nஎந்த ரைடு பற்றி மேலும் "
                    "தெரிந்துகொள்ள விரும்புகிறீர்கள்?"
                )

            else:

                heading = (
                    "Current ride prices:"
                )

                footer = (
                    "\n\nWhich ride would you like "
                    "to know more about?"
                )

            response = (
                heading
                + "\n\n"
                + "\n".join(lines)
                + footer
            )

        else:

            if language == "ml":

                response = (
                    "ക്ഷമിക്കണം, ഇപ്പോൾ സജീവമായ "
                    "റൈഡ് നിരക്കുകൾ ലഭ്യമല്ല."
                )

            elif language == "hi":

                response = (
                    "क्षमा करें, अभी कोई सक्रिय "
                    "राइड कीमत उपलब्ध नहीं है।"
                )

            elif language == "ta":

                response = (
                    "மன்னிக்கவும், தற்போது செயலில் உள்ள "
                    "ரைடு கட்டணங்கள் கிடைக்கவில்லை."
                )

            else:

                response = (
                    "Sorry, there are currently no "
                    "active ride prices available."
                )

        update_context(
            chat_session,
            last_intent="ride_price",
            awaiting="ride_selection",
        )

        return {
            "response": response,
            "intent": "ride_price",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 6. RIDE LIST
    # =====================================================

    if intent == "ride_list":

        rides = (
            Ride.objects
            .filter(
                is_active=True
            )
            .order_by("name")
        )

        ride_names = [
            f"• {ride.name}"
            for ride in rides
        ]

        if ride_names:

            if language == "ml":

                response = (
                    "ഞങ്ങളുടെ നിലവിലെ Flying Fox റൈഡുകൾ:\n\n"
                    + "\n".join(ride_names)
                    + "\n\nഏത് റൈഡിനെ കുറിച്ചാണ് അറിയേണ്ടത്?"
                )

            elif language == "hi":

                response = (
                    "हमारी उपलब्ध Flying Fox राइड्स:\n\n"
                    + "\n".join(ride_names)
                    + "\n\nआप किस राइड के बारे में जानना चाहेंगे?"
                )

            elif language == "ta":

                response = (
                    "தற்போது கிடைக்கும் Flying Fox ரைடுகள்:\n\n"
                    + "\n".join(ride_names)
                    + "\n\nஎந்த ரைடு பற்றி தெரிந்துகொள்ள விரும்புகிறீர்கள்?"
                )

            else:

                response = (
                    "Our currently available Flying Fox rides:\n\n"
                    + "\n".join(ride_names)
                    + "\n\nWhich one would you like to know more about?"
                )

        else:

            if language == "ml":
                response = "ഇപ്പോൾ സജീവമായ റൈഡുകൾ ലഭ്യമല്ല."

            elif language == "hi":
                response = "अभी कोई सक्रिय राइड उपलब्ध नहीं है।"

            elif language == "ta":
                response = "தற்போது செயலில் உள்ள ரைடுகள் இல்லை."

            else:
                response = "There are currently no active rides available."

        update_context(
            chat_session,
            last_intent="ride_list",
            awaiting="ride_selection",
        )

        return {
            "response": response,
            "intent": "ride_list",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 7. SAFETY
    # =====================================================

    if intent == "safety":

        response = get_response(
            "safety",
            language,
        )

        update_context(
            chat_session,
            last_intent="safety",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "safety",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 8. BOOKING
    # =====================================================

    if intent == "booking":

        response = get_response(
            "booking",
            language,
        )

        update_context(
            chat_session,
            last_intent="booking",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "booking",
            "response_type": "action",

            # Keep button in English as requested.
            "action_text": "Book Now",

            "action_url": "/bookings/",
            "show_quick_replies": True,
        }

    # =====================================================
    # 9. OFFERS
    # =====================================================

    if intent == "offers":

        if language == "ml":

            response = (
                "ഞങ്ങളുടെ നിലവിലെ ഓഫറുകളും ഡിസ്കൗണ്ടുകളും "
                "Offers പേജിൽ പരിശോധിക്കാം 😊"
            )

        elif language == "hi":

            response = (
                "आप हमारे मौजूदा ऑफर और डिस्काउंट "
                "Offers पेज पर देख सकते हैं 😊"
            )

        elif language == "ta":

            response = (
                "எங்களின் தற்போதைய சலுகைகள் மற்றும் "
                "தள்ளுபடிகளை Offers பக்கத்தில் பார்க்கலாம் 😊"
            )

        else:

            response = (
                "You can check our current Flying Fox "
                "offers and discounts on the Offers page 😊"
            )

        update_context(
            chat_session,
            last_intent="offers",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "offers",
            "response_type": "action",

            # Button stays English.
            "action_text": "View Offers",

            "action_url": "/offers/",
            "show_quick_replies": True,
        }

    # =====================================================
    # 10. QR TICKET
    # =====================================================

    if intent == "ticket":

        if language == "ml":

            response = (
                "ബുക്കിംഗും പേയ്മെന്റും വിജയകരമായി "
                "പൂർത്തിയായ ശേഷം നിങ്ങളുടെ QR ടിക്കറ്റ് ലഭിക്കും. 🎟️\n\n"
                "റൈഡിന് എത്തുമ്പോൾ QR ടിക്കറ്റ് കാണിക്കാം."
            )

        elif language == "hi":

            response = (
                "बुकिंग और पेमेंट सफलतापूर्वक पूरा होने के बाद "
                "आपको QR टिकट मिलेगा। 🎟️\n\n"
                "राइड पर पहुंचने पर QR टिकट दिखाएं।"
            )

        elif language == "ta":

            response = (
                "புக்கிங் மற்றும் பேமெண்ட் வெற்றிகரமாக முடிந்ததும் "
                "உங்கள் QR டிக்கெட் கிடைக்கும். 🎟️\n\n"
                "ரைடுக்கு வரும்போது QR டிக்கெட்டை காட்டுங்கள்."
            )

        else:

            response = (
                "Your QR ticket is provided after your booking "
                "and payment are completed successfully. 🎟️\n\n"
                "Show the QR ticket when you arrive for your ride."
            )

        update_context(
            chat_session,
            last_intent="ticket",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "ticket",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 11. PAYMENT
    # =====================================================

    if intent == "payment":

        if language == "ml":

            response = (
                "റൈഡ് ബുക്കിംഗ് സമയത്ത് ലഭ്യമായ "
                "ഓൺലൈൻ പേയ്മെന്റ് ഓപ്ഷനുകൾ ഉപയോഗിച്ച് "
                "പണമടയ്ക്കാം. 💳"
            )

        elif language == "hi":

            response = (
                "राइड बुक करते समय उपलब्ध ऑनलाइन "
                "पेमेंट विकल्पों से भुगतान कर सकते हैं। 💳"
            )

        elif language == "ta":

            response = (
                "ரைடு புக் செய்யும் போது கிடைக்கும் "
                "ஆன்லைன் பேமெண்ட் முறைகளை பயன்படுத்தி "
                "பணம் செலுத்தலாம். 💳"
            )

        else:

            response = (
                "You can pay using the available online "
                "payment options during the booking process. 💳"
            )

        update_context(
            chat_session,
            last_intent="payment",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "payment",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 12. LOCATION
    # =====================================================

    if intent == "location":

        if language == "ml":

            response = (
                "Flying Fox Adventure സ്ഥിതി ചെയ്യുന്നത് "
                "Thekkumkanam, Kerala-യിലാണ്. 📍"
            )

        elif language == "hi":

            response = (
                "Flying Fox Adventure Thekkumkanam, "
                "Kerala में स्थित है। 📍"
            )

        elif language == "ta":

            response = (
                "Flying Fox Adventure, Thekkumkanam, "
                "Kerala-வில் அமைந்துள்ளது. 📍"
            )

        else:

            response = (
                "Flying Fox Adventure is located at "
                "Thekkumkanam, Kerala. 📍"
            )

        update_context(
            chat_session,
            last_intent="location",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "location",
            "response_type": "text",
            "show_quick_replies": True,
        }

    # =====================================================
    # 13. HUMAN SUPPORT
    # =====================================================

    if intent == "human_help":

        if language == "ml":

            response = (
                "തീർച്ചയായും 😊 ഞങ്ങളുടെ Flying Fox ടീമുമായി "
                "നേരിട്ട് ബന്ധപ്പെടാം.\n\n"
                "📞 +91 7907219198\n"
                "✉️ adventureflyingfox@gmail.com"
            )

        elif language == "hi":

            response = (
                "ज़रूर 😊 आप हमारी Flying Fox टीम से "
                "सीधे संपर्क कर सकते हैं।\n\n"
                "📞 +91 7907219198\n"
                "✉️ adventureflyingfox@gmail.com"
            )

        elif language == "ta":

            response = (
                "நிச்சயமாக 😊 எங்கள் Flying Fox குழுவை "
                "நேரடியாக தொடர்பு கொள்ளலாம்.\n\n"
                "📞 +91 7907219198\n"
                "✉️ adventureflyingfox@gmail.com"
            )

        else:

            response = (
                "Sure 😊 You can contact our Flying Fox team directly.\n\n"
                "📞 +91 7907219198\n"
                "✉️ adventureflyingfox@gmail.com"
            )

        update_context(
            chat_session,
            last_intent="human_help",
            awaiting=None,
        )

        return {
            "response": response,
            "intent": "human_help",
            "response_type": "action",

            # Keep button English.
            "action_text": "Call Us",

            "action_url": "tel:+917907219198",
            "show_quick_replies": True,
        }


    # =====================================================
# PARKING
# =====================================================

    if intent == "parking":

       response = get_response(
        "parking",
        language,
    )

       update_context(
        chat_session,
        last_intent="parking",
        awaiting=None,
    )

       return {
        "response": response,
        "intent": "parking",
        "response_type": "text",
        "show_quick_replies": True,
    }

    # =====================================================
    # 14. FALLBACK
    # =====================================================

    response = get_response(
        "fallback",
        language,
    )

    update_context(
        chat_session,
        last_intent="fallback",
        awaiting=None,
    )

    return {
        "response": response,
        "intent": "fallback",
        "response_type": "text",
        "show_quick_replies": True,
    }