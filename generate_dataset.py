import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

PRODUCTS = [
    "Smartphone", "Laptop", "Tablet", "Smartwatch", "Wireless Headphones",
    "Monitor", "Printer", "Router", "External Hard Drive", "Webcam"
]

TICKET_TYPES = ["Technical Issue", "Billing Inquiry", "Product Inquiry", "Account Access", "General Query"]

PRIORITIES = ["Low", "Medium", "High", "Critical"]

CHANNELS = ["Email", "Phone", "Chat", "Social Media", "Web Form"]

SUBJECTS = {
    "Technical Issue": [
        "Device not turning on",
        "Software crash on startup",
        "Screen flickering issue",
        "Bluetooth connectivity problem",
        "Battery draining fast",
        "Overheating during usage",
        "Audio not working properly",
        "Camera malfunction",
        "Touchscreen unresponsive",
        "System update failed",
        "Wi-Fi keeps disconnecting",
        "Slow performance after update",
        "USB port not recognized",
        "Display showing wrong colors",
        "Keyboard keys not responding"
    ],
    "Billing Inquiry": [
        "Incorrect charge on my account",
        "Refund not received yet",
        "Double billing for subscription",
        "Payment method update issue",
        "Invoice not matching order",
        "Unexpected fee on statement",
        "Promo code not applied",
        "Subscription renewal charge",
        "Tax calculation seems wrong",
        "Need payment receipt"
    ],
    "Product Inquiry": [
        "Warranty coverage details",
        "Product specifications question",
        "Compatibility with accessories",
        "Available color options",
        "Expected delivery timeline",
        "Bulk purchase pricing",
        "Product comparison request",
        "Upgrade options available",
        "Return policy clarification",
        "Extended warranty options"
    ],
    "Account Access": [
        "Cannot login to my account",
        "Password reset not working",
        "Two-factor authentication issue",
        "Account locked after attempts",
        "Email verification not received",
        "Profile update not saving",
        "Cannot change email address",
        "Session keeps expiring",
        "Account merge request",
        "Unauthorized access detected"
    ],
    "General Query": [
        "Store location inquiry",
        "Service hours question",
        "Partnership opportunity",
        "Feedback on recent purchase",
        "How to contact support",
        "Shipping tracking question",
        "Corporate discount inquiry",
        "Gift card balance check",
        "Newsletter subscription",
        "Job application status"
    ]
}

DESCRIPTIONS = {
    "Technical Issue": {
        "High": [
            "My {product} has completely stopped working. It was fine yesterday but now it won't turn on at all. I've tried charging it for hours and pressing the power button multiple times. This is my primary work device and I need it urgently for important meetings tomorrow. Please help me resolve this immediately.",
            "The {product} I purchased last month is showing a critical error on screen and I cannot access any of my data. I have important files stored on it and I'm worried about data loss. The error message says 'System failure - contact support'. This is extremely urgent.",
            "My {product} overheated severely and shut down during an important presentation. When I try to restart it, there's a burning smell coming from the device. I'm concerned about safety and need immediate assistance. This has never happened before.",
            "After the latest system update, my {product} is completely bricked. It's stuck in a boot loop and nothing I try fixes it. I've lost access to all my work documents and have a critical deadline in two days. I need emergency support.",
            "The screen on my {product} cracked spontaneously without any impact or drop. There are visible lines across the display and touch functionality is completely gone. This appears to be a manufacturing defect and I need an urgent replacement."
        ],
        "Medium": [
            "I'm experiencing intermittent connectivity issues with my {product}. The Bluetooth keeps dropping connection every few minutes. I've tried resetting the device and re-pairing but the problem persists. It's becoming frustrating for daily use.",
            "The battery on my {product} is draining much faster than usual. It used to last the whole day but now it barely makes it to noon. I haven't installed any new apps recently. Could there be a software issue causing this?",
            "My {product} has been running very slowly since the last update. Apps take forever to open and there's noticeable lag when typing. I've cleared the cache and restarted multiple times but the performance hasn't improved.",
            "The camera on my {product} is producing blurry images even in good lighting conditions. The autofocus seems to be malfunctioning. I've cleaned the lens and restarted the device but the issue continues.",
            "The audio on my {product} is distorted when playing music or during calls. The speakers make a crackling sound at any volume level. I've tested with different apps and the problem is consistent across all of them."
        ],
        "Low": [
            "I noticed a minor cosmetic scratch on my {product} when I unboxed it. The device works fine otherwise but I wanted to report this for my records. It doesn't affect functionality at all.",
            "The notification light on my {product} blinks a different color than what's described in the manual. It shows amber instead of green. Everything else works perfectly, just wanted to check if this is normal.",
            "My {product} occasionally shows a small glitch when transitioning between apps. It's a very brief flicker that happens maybe once a day. Not a major issue but I thought I should report it.",
            "The default wallpaper on my {product} appears slightly different from what was shown in the advertisement. The device functions perfectly otherwise. Just curious if this is the correct version.",
            "I have a question about a specific setting on my {product}. The manual mentions a night mode feature but I can't seem to find it in the settings menu. Can you guide me to the right location?"
        ],
        "Critical": [
            "URGENT: My {product} is emitting smoke and making unusual sounds. I've immediately unplugged it and moved it away from other items. This could be a serious safety hazard. I need immediate attention and potentially a product recall check.",
            "My {product} containing all my business financial data has been compromised. I'm seeing unauthorized transactions and file modifications. This is a security breach that needs immediate investigation. Time-sensitive situation.",
            "The {product} exploded while charging overnight. Fortunately no one was hurt but there is damage to my furniture. This is a serious safety issue that needs urgent attention. I have photos of the damage and the device.",
            "Multiple {product} units in our office have simultaneously failed after a firmware update pushed by your company. This has brought our entire operations to a halt. We have 50 employees unable to work. Immediate resolution required.",
            "My {product} caught fire during normal use. The fire department was called and the incident has been documented. I need immediate contact from your safety team and information about recalls or known issues with this model."
        ]
    },
    "Billing Inquiry": {
        "High": [
            "I've been charged three times for the same {product} purchase. My credit card shows three separate transactions of the same amount on the same date. I need an immediate refund for the duplicate charges. My bank is asking for documentation.",
            "My account shows a charge of $2,499 for a {product} I never ordered. I suspect fraudulent activity on my account. I need this investigated immediately and the charge reversed. I've already contacted my bank.",
            "I cancelled my subscription two months ago but I'm still being charged monthly. I have the cancellation confirmation email as proof. I need all charges since cancellation to be refunded immediately.",
            "I was promised a full refund for my returned {product} three weeks ago but haven't received it yet. The return was confirmed received at your warehouse. My reference number is in the subject. I need this escalated.",
            "Your system charged me the full price even though I had a valid 50% discount code applied. The order confirmation shows the discount but my card was charged the full amount. I need the difference refunded right away."
        ],
        "Medium": [
            "I have a question about a small discrepancy on my latest invoice for the {product}. The tax amount seems slightly higher than what I calculated. Could you please review and confirm the correct amount?",
            "I'd like to update my payment method for my {product} subscription but the website keeps showing an error. I've tried multiple cards and browsers. Can you help me update it from your end?",
            "I received my invoice for the {product} but the billing address is wrong. I updated my address last month but the change doesn't seem to have taken effect. Can you correct this for future invoices?",
            "I'm confused about the pricing tiers for the {product} service plan. The website shows one price but the app shows a different one. Can you clarify which is the current correct pricing?",
            "My company needs itemized receipts for all {product} purchases made this quarter for tax purposes. Can you provide detailed invoices with individual item breakdowns?"
        ],
        "Low": [
            "I'm just checking whether my payment for the {product} went through successfully. My bank app shows it as pending. No rush, just want to confirm the status.",
            "Could you tell me when my next billing cycle for the {product} subscription starts? I'm planning my budget for next month and want to know the exact date.",
            "I noticed the currency symbol on my receipt for the {product} shows USD instead of CAD. The amount seems correct though. Just wanted to flag this for your records.",
            "I'm interested in switching from monthly to annual billing for my {product} plan. Could you let me know if there's a price difference and how to make the change?",
            "Could you send me a duplicate copy of my receipt for the {product} purchased last month? I need it for my expense report but seem to have misplaced the original email."
        ],
        "Critical": [
            "I'm seeing over $10,000 in unauthorized charges on my account for {product} purchases I never made. My account has clearly been hacked. I need all charges frozen and reversed immediately. I'm filing a police report.",
            "Your billing system has been charging my deceased mother's account for months after I notified you of her passing and requested account closure. This is causing significant distress. I need immediate resolution and full refund.",
            "We discovered your company has been systematically overcharging our enterprise account for {product} licenses. The total overcharge amounts to over $50,000 over the past year. We need an emergency audit and full reimbursement."
        ]
    },
    "Product Inquiry": {
        "High": [
            "I need urgent information about whether my {product} is compatible with the new operating system update before I proceed. If it's not compatible, I need to know my options immediately as I have a work deadline.",
            "My {product} warranty expires tomorrow and I need to know if the issue I'm experiencing is covered before it's too late. Can someone please review my case urgently?",
            "I placed a bulk order of 200 {product} units for my company and I need to confirm specifications before our procurement deadline today. The specifications on your website seem to have changed recently."
        ],
        "Medium": [
            "I'm considering purchasing the {product} and would like to know more about its specifications compared to the previous model. Specifically, I'm interested in battery life and processing power improvements.",
            "Could you tell me about the warranty coverage for the {product}? I want to know what's covered and for how long before making my purchase decision.",
            "I'm interested in purchasing the {product} but I need to know if it comes in different storage configurations. The website only shows one option but I've seen reviews mentioning multiple variants.",
            "I recently bought a {product} and I'm wondering about compatible accessories. Specifically, I need a protective case and a charging dock. Do you have official accessories available?",
            "What are the available color options for the {product}? The website shows three colors but I've seen advertisements with additional options. Are there region-specific variants?"
        ],
        "Low": [
            "Just curious about when the next generation of the {product} might be announced. I'm not in a hurry but I want to make an informed decision about buying the current model.",
            "I saw the {product} in a friend's home and I'd love to know more about it. Could you send me a product brochure or direct me to detailed specifications?",
            "Does the {product} come with a user manual in Spanish? My parents would like one and they're more comfortable reading in Spanish.",
            "I'm writing a blog review about the {product} and would like to verify some specifications. Could you confirm the exact dimensions and weight listed on the spec sheet?",
            "Is the {product} packaging made from recycled materials? I'm environmentally conscious and would like to know about your sustainability practices."
        ],
        "Critical": [
            "Our hospital just purchased 500 {product} units for patient monitoring. We've discovered the specifications don't match what was promised in the contract. Patient safety may be at risk. We need immediate clarification."
        ]
    },
    "Account Access": {
        "High": [
            "I'm locked out of my account and I have critical work documents stored in my cloud storage linked to the {product}. I've tried password reset but the verification emails aren't arriving. I have a deadline in 4 hours.",
            "Someone has changed my account password and recovery email for my {product} account. I can no longer access any of my services. I believe my account has been compromised and need immediate recovery.",
            "I'm getting notifications that someone is trying to access my {product} account from an unknown location. I've changed my password but the attempts continue. I'm worried about my personal data security.",
            "My business account managing multiple {product} devices for our team has been suspended without explanation. Our entire team of 25 people can't access their work resources. We need this restored immediately."
        ],
        "Medium": [
            "I'm having trouble setting up two-factor authentication on my {product} account. The QR code won't scan and the manual entry code gives an error. I'd like to get this security feature enabled.",
            "I changed my phone number recently and now I can't receive verification codes for my {product} account. I'd like to update my phone number but the security settings require the old number for verification.",
            "My {product} account profile shows incorrect information that I can't seem to edit through the normal settings. The name and email fields are grayed out. How can I update my personal details?",
            "I'm trying to merge my two {product} accounts into one. I accidentally created a duplicate account with a different email. Can you help me consolidate them while keeping all my purchase history?",
            "The session on my {product} account keeps expiring every few minutes, forcing me to log in repeatedly. I've cleared cookies and tried different browsers but the issue persists."
        ],
        "Low": [
            "I'd like to change my display name on my {product} account. It currently shows my full name but I prefer to use just my first name. Where can I find this setting?",
            "I forgot my account password for the {product} portal. I'm not in a rush as I can access it from my phone, but I'd like to reset it when convenient.",
            "Can I add a secondary email address to my {product} account? I'd like to receive notifications on my work email as well as my personal one.",
            "I'm curious about the privacy settings on my {product} account. I'd like to review what data is being collected and how it's used. Where can I find the privacy dashboard?",
            "How do I download all my data from my {product} account? I'd like to keep a personal backup of my account information for my records."
        ],
        "Critical": [
            "EMERGENCY: Our corporate admin account for {product} has been breached. The attacker has changed all admin credentials and is actively deleting employee accounts. We need your security team to freeze our organization's account NOW.",
            "My {product} account linked to my banking information has been compromised. I can see the attacker has already accessed my financial details. I need account freeze and security investigation immediately."
        ]
    },
    "General Query": {
        "High": [
            "I need to find the nearest authorized service center for my {product} urgently. The device needs repair and I can't find updated service center information on your website. I'm in a remote area.",
            "I have a meeting with your sales team today but haven't received the meeting link or confirmation. The meeting is about a large enterprise deal for {product} units. Can someone confirm the schedule?"
        ],
        "Medium": [
            "I'd like to provide feedback about my recent experience purchasing the {product}. The sales representative was very helpful but the checkout process on the website was confusing.",
            "I'm interested in your corporate discount program for bulk {product} purchases. Our company is planning to outfit our new office and would like to know about volume pricing.",
            "Could you provide information about your company's recycling program? I have an old {product} that I'd like to dispose of responsibly.",
            "I need help tracking my {product} shipment. The tracking number provided doesn't seem to work on the shipping carrier's website. My order was placed five days ago.",
            "I received a promotional email about a {product} sale but the link in the email leads to a 404 error page. Could you provide the correct link to the sale?"
        ],
        "Low": [
            "I'm just writing to say how happy I am with my {product} purchase. It has exceeded my expectations and I wanted to share my positive experience.",
            "Do you have any upcoming events or product launch events for the {product} line? I'm a tech enthusiast and would love to attend.",
            "I noticed a typo on the {product} page of your website. The word 'specifications' is misspelled as 'specificatons'. Just thought I'd let you know.",
            "Could you tell me about the history of your company? I'm doing a school project about technology companies and would love to include information about your brand.",
            "I'd like to know if you have a referral program. I've recommended the {product} to several friends and it would be nice if there were rewards for referrals."
          ],
        "Critical": [
            "Your website appears to be leaking customer personal data. I found what appears to be a database dump publicly accessible through a URL pattern on your {product} support pages. This is a major security vulnerability that needs immediate attention."
        ]
    }
}

CUSTOMER_FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Ahmed", "Fatima",
    "Wei", "Priya", "Carlos", "Yuki", "Omar", "Aisha", "Raj", "Elena"
]

CUSTOMER_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Khan", "Patel", "Chen", "Singh", "Kim", "Tanaka", "Ali", "Sharma", "Santos", "Ivanov"
]


def generate_tickets(n_tickets=8000):
    """Generate synthetic customer support tickets."""
    tickets = []

    priority_weights = {
        "Technical Issue": [0.20, 0.35, 0.30, 0.15],
        "Billing Inquiry": [0.25, 0.35, 0.30, 0.10],
        "Product Inquiry": [0.35, 0.40, 0.20, 0.05],
        "Account Access": [0.20, 0.30, 0.35, 0.15],
        "General Query": [0.40, 0.35, 0.20, 0.05]
    }

    type_weights = [0.30, 0.20, 0.20, 0.15, 0.15]

    for i in range(n_tickets):
        ticket_type = np.random.choice(TICKET_TYPES, p=type_weights)
        priority = np.random.choice(PRIORITIES, p=priority_weights[ticket_type])
        product = random.choice(PRODUCTS)
        channel = random.choice(CHANNELS)
        subject = random.choice(SUBJECTS[ticket_type])

        available_descriptions = DESCRIPTIONS[ticket_type].get(priority, DESCRIPTIONS[ticket_type]["Medium"])
        description_template = random.choice(available_descriptions)
        description = description_template.format(product=product)

        first_name = random.choice(CUSTOMER_FIRST_NAMES)
        last_name = random.choice(CUSTOMER_LAST_NAMES)
        customer_name = f"{first_name} {last_name}"

        ticket = {
            "Ticket ID": f"TICKET-{10001 + i}",
            "Customer Name": customer_name,
            "Customer Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Product Purchased": product,
            "Ticket Type": ticket_type,
            "Ticket Subject": subject,
            "Ticket Description": description,
            "Ticket Priority": priority,
            "Ticket Channel": channel
        }
        tickets.append(ticket)

    return pd.DataFrame(tickets)


if __name__ == "__main__":
    print("=" * 60)
    print("  GENERATING SUPPORT TICKET DATASET")
    print("=" * 60)

    df = generate_tickets(8000)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support_tickets.csv")
    df.to_csv(output_path, index=False)

    print(f"\nDataset saved to: {output_path}")
    print(f"Total tickets: {len(df)}")
    print(f"\nTicket Type Distribution:")
    print(df["Ticket Type"].value_counts().to_string())
    print(f"\nPriority Distribution:")
    print(df["Ticket Priority"].value_counts().to_string())
    print(f"\nSample ticket:")
    print(df.iloc[0].to_string())
    print("\nDone!")
