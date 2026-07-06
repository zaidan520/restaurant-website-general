import logging

def send_whatsapp_message(data: dict, code: str, to_number: str):
    message = f"""[WHATSAPP MESSAGE to {to_number}]
New Booking Alert!
Code: {code}
Name: {data.get('name')}
Phone: {data.get('phone')}
Party Size: {data.get('party_size')} guests
Date: {data.get('date')}
Time: {data.get('time')}
Notes: {data.get('notes', '')}
"""
    logging.info(f"WhatsApp message dispatched to {to_number}")
    print(f"\n--- WHATSAPP SIMULATOR ---\n{message}---------------------------\n")
