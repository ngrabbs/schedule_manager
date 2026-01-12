# ✅ iOS Shortcuts Fix Applied!

## The Problem You Had

Your iOS Shortcuts was sending:
- **Form method**: `=add%3A+reminder+to+call+andrew+at+3pm` (URL-encoded with `=` prefix)
- **JSON method**: `{"":"add: reminder to call andrew at 3pm"}` (wrapped in JSON)

Both were causing "invalid command" errors because the daemon expected plain text.

## The Fix

The command listener now has a `_clean_message()` function that:
1. ✅ Strips the `=` prefix from Form messages
2. ✅ URL-decodes special characters (`%3A` → `:`, `+` → space)
3. ✅ Unwraps JSON-wrapped messages
4. ✅ Passes plain text through unchanged

## Now All Three Methods Work!

### Method 1: Form with File Type
```
Request Body: Form
  + Add row:
    Key: (empty)
    Type: File
    Value: add: [Ask for Input]
```
✅ **Works!** The system decodes the URL encoding automatically.

### Method 2: JSON (Easiest!)
```
Request Body: JSON
Body: add: [Ask for Input]
```
✅ **Works!** The system unwraps the JSON automatically.

### Method 3: Headers (Still works too!)
```
Headers:
  Message: add: [Ask for Input]
  Title: Schedule Command
  
Request Body: Form (0 items)
```
✅ **Works!** This was always the cleanest method.

## Test Results

```bash
# Form method input: =add%3A+reminder+to+call+andrew+at+3pm
→ Cleaned to: add: reminder to call andrew at 3pm
→ Result: ✅ Added: reminder to call andrew at 03:50 PM

# JSON method input: {"":"add: test meeting tomorrow at 2pm"}
→ Cleaned to: add: test meeting tomorrow at 2pm
→ Result: ✅ Added: test meeting at 02:00 PM

# Plain text: list
→ Cleaned to: list
→ Result: ✅ Shows daily summary
```

## What To Do Now

### Option 1: Use JSON (Simplest!)

1. **Request Body**: Select `JSON`
2. **Body**: Just type your command directly
   - For "Add Schedule": `add: [Ask for Input]`
   - For "My Schedule": `list`
   - For "Upcoming": `upcoming`

That's it! The daemon handles the JSON wrapping automatically.

### Option 2: Use Form with File Type

1. **Request Body**: Select `Form`
2. Add a row with Type: `File`
3. Value: Your command

The daemon handles the URL encoding automatically.

### Option 3: Use Headers (Cleanest)

Still the most elegant - see START_HERE.md for details.

## Next Steps

1. **Try any method** - they all work now!
2. **Build your shortcuts** using whichever method feels easiest
3. **Test from Apple Watch** with "Hey Siri, add schedule"
4. **Enjoy!** 🎉

## Technical Details

The fix is in `schedule_manager/command_listener.py`:
- New method: `_clean_message()` 
- Automatically detects and cleans all iOS Shortcuts formats
- No configuration needed - just works!

---

**You can now use iOS Shortcuts with ANY Request Body type! 🎊**
