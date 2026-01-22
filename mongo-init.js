// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the meghan_chat database
db = db.getSiblingDB('meghan_chat');

// Create a user for the application
db.createUser({
  user: 'meghan_user',
  pwd: 'meghan_password',
  roles: [
    {
      role: 'readWrite',
      db: 'meghan_chat'
    }
  ]
});

// Create initial collections with validation
db.createCollection('chat_sessions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'mode', 'started_at'],
      properties: {
        user_id: { bsonType: 'string' },
        mode: { 
          bsonType: 'string',
          enum: ['talk', 'plan', 'calm', 'reflect']
        },
        started_at: { bsonType: 'date' },
        ended_at: { bsonType: 'date' },
        messages: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['role', 'content', 'timestamp'],
            properties: {
              role: { 
                bsonType: 'string',
                enum: ['user', 'assistant']
              },
              content: { bsonType: 'string' },
              timestamp: { bsonType: 'date' }
            }
          }
        }
      }
    }
  }
});

db.createCollection('wellbeing_data', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'week_starting'],
      properties: {
        user_id: { bsonType: 'string' },
        week_starting: { bsonType: 'date' },
        mood_entries: { bsonType: 'array' },
        journal_entries: { bsonType: 'array' },
        insights: { bsonType: 'object' }
      }
    }
  }
});

// Create indexes for better performance
db.chat_sessions.createIndex({ 'user_id': 1, 'started_at': -1 });
db.wellbeing_data.createIndex({ 'user_id': 1, 'week_starting': -1 });

print('MongoDB initialization completed successfully');