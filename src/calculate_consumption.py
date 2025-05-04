import re

def convert_token_value(value, unit):
    unit = unit.lower()
    if unit == 'k':
        return value * 1000
    elif unit == 'm':
        return value * 1e6
    else:
        return value

total_sent = 0.0
total_received = 0.0
total_message_cost = 0.0
total_session_cost = 0.0

# indicate a .aider.chat.history.md path
file_path=

token_pattern = re.compile(r'>\s*Tokens:\s*([\d.]+)([kKmM]?)\s*sent,\s*([\d.]+)([kKmM]?)\s*received')

cost_pattern = re.compile(r'Cost:\s*\$?\s*([\d.]+)\s*message,\s*\$?\s*([\d.]+)\s*session')

with open(file_path, 'r', encoding='Utf-8') as file:  
    for line in file:
        line = line.strip()
        
        token_match = token_pattern.search(line)
        if token_match:
            sent_val = float(token_match.group(1))
            sent_unit = token_match.group(2).lower()
            total_sent += convert_token_value(sent_val, sent_unit)

            received_val = float(token_match.group(3))
            received_unit = token_match.group(4).lower()
            total_received += convert_token_value(received_val, received_unit)

       
        cost_match = cost_pattern.search(line)
        if cost_match:
            total_message_cost += float(cost_match.group(1))
            total_session_cost += float(cost_match.group(2))


print(f"Total sent tokens: {int(total_sent)}")
print(f"Total received tokens: {int(total_received)}")
print(f"Total message cost: ${total_message_cost:.2f}")
print(f"Total session cost: ${total_session_cost:.2f}")
print(f"Total cost: ${(total_message_cost + total_session_cost):.2f}")