# Voice Commands with Siri

Control your schedule by talking to Siri on your iPhone or Apple Watch.

## Setup (5 minutes)

### Prerequisites

1. Schedule manager daemon running on your server
2. ntfy.sh app installed on your iPhone
3. Subscribed to your notification topic in ntfy app

### Create the Shortcut

You only need **ONE shortcut** for everything:

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create new shortcut
3. Add these actions:

**Action 1: Dictate Text**
- Search "Dictate Text" and add it
- This captures what you say

**Action 2: Get Contents of URL**
- Search "Get Contents of URL" and add it
- Configure:
  - **URL**: `https://ntfy.sh/YOUR_COMMANDS_TOPIC`
  - **Method**: POST
  - **Request Body**: File
  - **File**: Select "Dictated Text" variable

4. **Name the shortcut**: "Schedule"
5. Tap the **(i)** button → **Add to Siri**
6. Record: **"Hey Siri, Schedule"**

### Test It

1. Say "Hey Siri, Schedule"
2. When prompted, say "What's on my schedule today"
3. Check your phone for the notification response

## Usage

Just speak naturally after saying "Hey Siri, Schedule":

### Adding Tasks

```
"Add dentist appointment Friday at 10am"
"Remind me to call mom tomorrow at 3pm"
"Meeting with Bob next Monday at 2pm for 1 hour"
"Pick up groceries this afternoon"
```

### Viewing Schedule

```
"What's on my schedule today"
"What do I have tomorrow"
"Show me this week"
"What's coming up"
```

### Managing Tasks

```
"Complete task 5"
"Delete task 12"
"Reschedule task 3 to 4pm"
"Mark the dentist appointment done"
```

### Priority

Say "urgent" or "important" for multiple reminders:

```
"Add urgent client call at 3pm"
→ You'll get reminders at 2:45, 2:55, and 3:00

"Add call mom at 3pm"
→ Single reminder at 3:00
```

## Apple Watch

The shortcut automatically syncs to your Apple Watch.

**Method 1: Siri**
- Raise wrist
- "Hey Siri, Schedule"
- Speak your command

**Method 2: Complication**
- Add Shortcuts complication to watch face
- Tap to run instantly

## How It Works

```
Your voice
    ↓
Siri transcribes
    ↓
Shortcut sends to ntfy.sh
    ↓
Your server receives command
    ↓
AI agent processes naturally
    ↓
Task created in database
    ↓
Confirmation sent via ntfy.sh
    ↓
Notification on your phone
```

The AI agent understands natural language - no special syntax or prefixes needed.

## Tips

### For Better Recognition

- Speak clearly, especially times: "three PM" not "3pm"
- Use natural phrasing: "remind me to" works great
- Be specific with dates: "next Tuesday" or "January 15th"

### Response Time

- Expect 5-10 seconds for the full round trip
- The notification confirms what was created
- Check the time/date in the confirmation

### If Something Goes Wrong

- The AI will do its best to understand
- Check the notification for what was actually created
- You can always delete and try again

## Troubleshooting

### Siri says "I can't do that"

- Make sure the shortcut is properly added to Siri
- Try re-recording the Siri phrase
- Check shortcut runs manually first

### No response notification

1. Check daemon is running on your server
2. Check you're subscribed to the notification topic (not commands topic)
3. Test manually:
   ```bash
   curl -d "what's on my schedule" https://ntfy.sh/YOUR_COMMANDS_TOPIC
   ```

### Wrong time parsed

Try being more explicit:
- Instead of "at 3" say "at 3pm"
- Instead of "tomorrow afternoon" say "tomorrow at 2pm"

### Command not understood

The AI handles most natural language, but if it fails:
- Rephrase more simply
- Break into separate commands
- Check daemon logs for errors

## Security

Your commands topic is like a password:
- Don't share the shortcut with others (it contains your topic)
- Don't post screenshots showing the topic
- Use a random, unguessable topic name

## Alternative: Multiple Shortcuts

If you prefer dedicated shortcuts for common actions:

**Quick Add** (skips dictation prompt):
1. Create shortcut
2. Action: "Ask for Input" → "What should I add?"
3. Action: "Get Contents of URL" with the input

**Today's Schedule** (no voice needed):
1. Create shortcut  
2. Action: "Get Contents of URL"
3. Body: "what's on my schedule today"

But honestly, the single "Schedule" shortcut handles everything!
