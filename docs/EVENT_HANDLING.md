# DSA Agent Event Handling Documentation

This document describes how the DSA Agent handles different types of events during agent execution and how they're displayed in the Streamlit UI.

## Overview

The DSA Agent now provides comprehensive event handling for all stages of agent execution, from initial run start to completion, including detailed information about reasoning steps, tool calls, and memory updates.

## Event Types Handled

### 1. Run Management Events

#### `RunStarted`

- **Trigger**: When agent execution begins
- **UI Display**: Green status indicator showing "🚀 Started" with model name
- **Data**: Model name and provider information

#### `RunCompleted`

- **Trigger**: When agent execution finishes successfully
- **UI Display**: Green status indicator showing "✅ Completed"
- **Data**: Final content, reasoning content, and thinking information
- **Special Features**: Shows final reasoning in an expandable section if available

#### `RunError`

- **Trigger**: When an error occurs during execution
- **UI Display**: Red error status with error message
- **Data**: Error message details
- **Special Features**: Replaces main response with error information

#### `RunCancelled`

- **Trigger**: When execution is cancelled
- **UI Display**: Warning status showing cancellation reason
- **Data**: Cancellation reason

#### `RunPaused`

- **Trigger**: When execution pauses (e.g., for tool confirmation)
- **UI Display**: Warning status showing pause reason
- **Data**: List of tools requiring confirmation

#### `RunContinued`

- **Trigger**: When execution resumes after pause
- **UI Display**: Info status showing "▶️ Continued"
- **Data**: Basic event information

### 2. Content Events

#### `RunResponseContent`

- **Trigger**: When the agent produces content during execution
- **UI Display**: Real-time content streaming with typing indicator
- **Data**: Content text, content type, thinking information
- **Special Features**: Shows thinking information in a separate info box

### 3. Reasoning Events

#### `ReasoningStarted`

- **Trigger**: When reasoning process begins
- **UI Display**: Blue status indicator showing "🧠 Reasoning..."
- **Data**: Basic event information

#### `ReasoningStep`

- **Trigger**: For each step in the reasoning process
- **UI Display**: Reasoning content in expandable sections
- **Data**: Step content and detailed reasoning information
- **Special Features**: Each step can be expanded to view detailed reasoning

#### `ReasoningCompleted`

- **Trigger**: When reasoning process completes
- **UI Display**: Green status indicator showing "✅ Reasoning Complete"
- **Data**: Final reasoning content

### 4. Tool Execution Events

#### `ToolCallStarted`

- **Trigger**: When a tool begins execution
- **UI Display**: Blue status showing tool name being used
- **Data**: Tool information (name, type, description)
- **Special Features**: Shows active tool indicator in main content area

#### `ToolCallCompleted`

- **Trigger**: When a tool finishes execution
- **UI Display**: Green status showing tool completion
- **Data**: Tool information and execution results
- **Special Features**:
  - Shows tool results in expandable sections
  - Results are truncated for display (first 500 characters)
  - Clears active tool indicators when all tools complete

### 5. Memory Management Events

#### `MemoryUpdateStarted`

- **Trigger**: When memory update process begins
- **UI Display**: Blue status indicator showing "💾 Updating Memory..."
- **Data**: Basic event information

#### `MemoryUpdateCompleted`

- **Trigger**: When memory update completes
- **UI Display**: Green status indicator showing "✅ Memory Updated"
- **Data**: Basic event information

## UI Components

### Status Bar

The status bar contains four status indicators:

1. **Run Status**: Overall execution status
2. **Reasoning Status**: Reasoning process status
3. **Tool Status**: Active tool execution status
4. **Memory Status**: Memory update status

### Content Areas

1. **Main Content**: Streamed agent responses with typing indicators
2. **Thinking Display**: Shows model's internal thoughts
3. **Tool Information**: Shows currently active tools
4. **Expandable Sections**:
   - Reasoning steps
   - Tool results
   - Final reasoning summaries

### Debug Mode

When "Show Event Details" is enabled:

- Each event displays a debug expandable section
- Shows raw event data in JSON format
- Useful for development and troubleshooting

## Implementation Details

### DSA Agent (`dsa_agent.py`)

The agent processes each event and creates structured data:

```python
event_data = {
    "event_type": event.event,
    "timestamp": getattr(event, 'created_at', None),
    "agent_id": getattr(event, 'agent_id', None),
    "run_id": getattr(event, 'run_id', None),
    "session_id": getattr(event, 'session_id', None),
}
```

Key features:

- Safe attribute extraction using `getattr()`
- Tool information serialization with `_safe_get_tool_info()`
- Content truncation for large results
- Structured event data format

### Streamlit UI (`app.py`)

The UI handles events with:

- Real-time status updates
- Content streaming with visual indicators
- Expandable sections for detailed information
- Automatic cleanup of temporary UI elements
- Error handling and graceful degradation

## Error Handling

### Agent Level

- Catches and logs all exceptions during event processing
- Provides fallback for unknown event types
- Safe attribute extraction prevents crashes

### UI Level

- Graceful handling of malformed event data
- Error status indicators for failed operations
- Fallback content for missing information
- Automatic cleanup on errors

## Configuration Options

### Sidebar Settings

1. **Debug Mode**: Enables detailed logging in the agent
2. **Show Event Details**: Displays raw event data for debugging
3. **Model Selection**: Choose the AI model for execution

### Session Management

- New session creation clears all event history
- Session information display for debugging
- Persistent agent configuration across interactions

## Best Practices

### For Development

1. Enable "Show Event Details" during development
2. Monitor logs for detailed event information
3. Test with different event scenarios

### For Production

1. Disable debug modes for performance
2. Monitor error events for system health
3. Use truncated results display for large outputs

## Future Enhancements

Potential improvements:

1. Event filtering and search
2. Export event logs
3. Real-time event statistics
4. Custom event handlers
5. Event replay functionality

## Troubleshooting

### Common Issues

1. **Missing Events**: Check agent configuration and MCP tools
2. **UI Not Updating**: Verify event structure and data types
3. **Tool Information Missing**: Check `_safe_get_tool_info()` implementation
4. **Memory Leaks**: Ensure proper cleanup of UI elements

### Debug Steps

1. Enable debug mode and event details
2. Check browser console for JavaScript errors
3. Review agent logs for event processing issues
4. Verify event data structure matches expected format
