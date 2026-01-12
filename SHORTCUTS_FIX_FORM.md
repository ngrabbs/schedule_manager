# iOS Shortcuts: The Form Fix (Based on Your Screenshot)

## What You're Seeing

Your screenshot shows the **Request Body: Form** section with three columns:
- **Key**
- **Type** ← The key to success!
- **Value**

There's no "plain text mode" - instead, you use the **Type** column!

---

## ✅ The Solution: Use Form with File Type

### Step-by-Step

1. **Keep Request Body set to `Form`** (as shown in your screenshot)

2. **Tap the `+` button** (bottom left of the Request Body section) to add a new form field

3. **Fill in the new row:**
   - **Key**: Leave it **empty** (or type "body" - doesn't matter)
   - **Type**: Tap this column and select **"File"** from the menu
   - **Value**: Type `add: ` then tap to insert the **[Ask for Input]** variable

4. **Final result should look like:**
   ```
   Key: (empty)
   Type: File
   Value: add: [Ask for Input icon]
   ```

### Why This Works

When you set Type to "File", iOS Shortcuts sends the Value as raw content in the HTTP body, which is exactly what ntfy.sh expects!

---

## Alternative: Skip Request Body, Use Headers Only

ntfy.sh can also receive the message via headers instead of body!

### Method: Message in Headers

1. **Request Body**: Leave as `Form` with **0 items** (don't add anything)

2. **Headers section** (tap the `+` button there):
   - Key: `Message`
   - Value: `add: [Ask for Input]`
   
3. **Also add these headers:**
   - Key: `Title`
   - Value: `Schedule Command`

This sends your command in the `Message` header, which ntfy.sh will read!

### Complete Headers-Only Config

```
Headers:
  Key: Message    Value: add: [Ask for Input]
  Key: Title      Value: Schedule Command
  
Request Body: Form (0 items)
```

**This is actually easier and works great!**

---

## Testing Your Configuration

### Quick Test: Send "help" Command

1. **Create a simple test shortcut:**
   - Add action: "Get Contents of URL"
   - URL: `https://ntfy.sh/nick_cmd_a1ask10h`
   - Method: `POST`
   - Request Body: Form with Type: File, Value: `help`

2. **Run it** - you should get a notification with available commands!

### Test with Variable

Once the simple test works:
1. Add "Ask for Input" action before "Get Contents of URL"
2. Change Value from `help` to `add: [Ask for Input]`
3. Run and type: "test tomorrow at 3pm"

---

## Recommended Approach for All Shortcuts

Based on your iOS version, I recommend the **Headers method** because it's cleaner:

### "Add Schedule" Shortcut

```
Action 1: Ask for Input
  - Prompt: "What should I schedule?"

Action 2: Get Contents of URL
  - URL: https://ntfy.sh/nick_cmd_a1ask10h
  - Method: POST
  - Headers:
      Message: add: [Provided Input]
      Title: Schedule Command
  - Request Body: Form (0 items)
```

### "My Schedule" Shortcut

```
Action: Get Contents of URL
  - URL: https://ntfy.sh/nick_cmd_a1ask10h
  - Method: POST
  - Headers:
      Message: list
      Title: Schedule Query
  - Request Body: Form (0 items)
```

### "What's Coming Up" Shortcut

```
Action: Get Contents of URL
  - URL: https://ntfy.sh/nick_cmd_a1ask10h
  - Method: POST
  - Headers:
      Message: upcoming
      Title: Schedule Query
  - Request Body: Form (0 items)
```

---

## Why Both Methods Work

ntfy.sh accepts messages in two ways:

1. **HTTP Body** (what we tried first):
   ```
   POST /topic
   Body: "your message here"
   ```

2. **HTTP Header** (easier with iOS Shortcuts):
   ```
   POST /topic
   Header: Message: your message here
   ```

Both deliver the same result - your daemon receives the command and processes it!

---

## Summary: Two Working Methods

### Method A: Form with File Type
```
Request Body: Form
  Key: (empty)
  Type: File
  Value: add: [Ask for Input]
```

### Method B: Headers Only (Easier!)
```
Headers:
  Message: add: [Ask for Input]
  Title: Schedule Command
  
Request Body: Form (0 items)
```

**I recommend Method B** - it's simpler and avoids the Form complexity entirely!

---

## Try It Now!

1. Create a quick test shortcut using **Method B** (Headers only)
2. Send the command: `help`
3. Check your notifications
4. If it works, you're all set! Build the rest of your shortcuts the same way.

Let me know which method works for you!
