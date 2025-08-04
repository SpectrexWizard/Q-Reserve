#!/usr/bin/env python3
"""
Demo script for the Helpdesk System MVP.
This script demonstrates the API capabilities of the system.
"""

import requests
import json
import time

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
DEMO_ADMIN = {'email': 'admin@helpdesk.local', 'password': 'admin123'}

def make_request(method, endpoint, data=None, token=None):
    """Make an API request with proper headers."""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {BASE_URL}")
        print("   Make sure the server is running with: python run.py")
        return None

def demo_authentication():
    """Demonstrate user authentication."""
    print("\n🔐 Testing Authentication...")
    
    # Test admin login
    response = make_request('POST', '/auth/login', DEMO_ADMIN)
    if response and response.status_code == 200:
        data = response.json()
        print("✅ Admin login successful")
        return data.get('access_token')
    else:
        print("❌ Admin login failed")
        if response:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
        return None

def demo_user_registration():
    """Demonstrate user registration."""
    print("\n👤 Testing User Registration...")
    
    test_user = {
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'testpass123',
        'role': 'end_user'
    }
    
    response = make_request('POST', '/auth/register', test_user)
    if response and response.status_code == 201:
        print("✅ User registration successful")
        return response.json().get('access_token')
    else:
        print("❌ User registration failed")
        if response:
            error = response.json().get('error', 'Unknown error')
            if 'already registered' in error or 'already taken' in error:
                print("   ℹ️  User already exists, trying login...")
                login_data = {'email': test_user['email'], 'password': test_user['password']}
                login_response = make_request('POST', '/auth/login', login_data)
                if login_response and login_response.status_code == 200:
                    print("✅ User login successful")
                    return login_response.json().get('access_token')
            print(f"   Error: {error}")
        return None

def demo_categories(admin_token):
    """Demonstrate category management."""
    print("\n📁 Testing Category Management...")
    
    # Create a test category
    category_data = {
        'name': 'Demo Category',
        'description': 'A category created by the demo script'
    }
    
    response = make_request('POST', '/categories/create', category_data, admin_token)
    if response and response.status_code == 201:
        print("✅ Category creation successful")
        return response.json().get('category', {}).get('id')
    else:
        print("❌ Category creation failed")
        if response:
            error = response.json().get('error', 'Unknown error')
            if 'already exists' in error:
                print("   ℹ️  Category already exists")
                # Try to get existing categories
                categories_response = make_request('GET', '/categories/', token=admin_token)
                if categories_response and categories_response.status_code == 200:
                    categories = categories_response.json().get('categories', [])
                    for cat in categories:
                        if cat['name'] == 'Demo Category':
                            return cat['id']
            print(f"   Error: {error}")
        return None

def demo_ticket_creation(user_token, category_id):
    """Demonstrate ticket creation."""
    print("\n🎫 Testing Ticket Creation...")
    
    ticket_data = {
        'subject': 'Demo Ticket - API Test',
        'description': 'This is a test ticket created by the demo script to showcase the API functionality.',
        'category_id': category_id,
        'priority': 'medium'
    }
    
    response = make_request('POST', '/tickets/create', ticket_data, user_token)
    if response and response.status_code == 201:
        print("✅ Ticket creation successful")
        ticket = response.json().get('ticket', {})
        print(f"   Ticket ID: {ticket.get('id')}")
        print(f"   Subject: {ticket.get('subject')}")
        return ticket.get('id')
    else:
        print("❌ Ticket creation failed")
        if response:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
        return None

def demo_comments(user_token, ticket_id):
    """Demonstrate comment system."""
    print("\n💬 Testing Comment System...")
    
    comment_data = {
        'ticket_id': ticket_id,
        'content': 'This is a test comment added via the API.'
    }
    
    response = make_request('POST', '/comments/create', comment_data, user_token)
    if response and response.status_code == 201:
        print("✅ Comment creation successful")
        return response.json().get('comment', {}).get('id')
    else:
        print("❌ Comment creation failed")
        if response:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
        return None

def demo_voting(user_token, ticket_id):
    """Demonstrate voting system."""
    print("\n👍 Testing Voting System...")
    
    # Upvote the ticket
    vote_data = {
        'ticket_id': ticket_id,
        'is_upvote': True
    }
    
    response = make_request('POST', '/votes/toggle', vote_data, user_token)
    if response and response.status_code == 200:
        print("✅ Upvote successful")
        vote_info = response.json()
        print(f"   Vote score: {vote_info.get('vote_score', 0)}")
        return True
    else:
        print("❌ Voting failed")
        if response:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
        return False

def demo_ticket_status_update(admin_token, ticket_id):
    """Demonstrate ticket status updates."""
    print("\n🔄 Testing Ticket Status Update...")
    
    update_data = {
        'status': 'in_progress'
    }
    
    response = make_request('POST', f'/tickets/{ticket_id}/update', update_data, admin_token)
    if response and response.status_code == 200:
        print("✅ Ticket status update successful")
        ticket = response.json().get('ticket', {})
        print(f"   New status: {ticket.get('status', 'Unknown')}")
        return True
    else:
        print("❌ Ticket status update failed")
        if response:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
        return False

def main():
    """Run the complete demo."""
    print("🚀 Helpdesk System API Demo")
    print("=" * 40)
    
    # Test basic connectivity
    response = make_request('GET', '/auth/login')
    if not response:
        return
    
    # Run demo steps
    admin_token = demo_authentication()
    if not admin_token:
        print("\n❌ Cannot continue without admin authentication")
        return
    
    user_token = demo_user_registration()
    if not user_token:
        print("\n❌ Cannot continue without user authentication")
        return
    
    category_id = demo_categories(admin_token)
    if not category_id:
        print("\n❌ Cannot continue without a category")
        return
    
    ticket_id = demo_ticket_creation(user_token, category_id)
    if not ticket_id:
        print("\n❌ Cannot continue without a ticket")
        return
    
    comment_id = demo_comments(user_token, ticket_id)
    vote_success = demo_voting(user_token, ticket_id)
    status_update_success = demo_ticket_status_update(admin_token, ticket_id)
    
    # Summary
    print("\n📊 Demo Summary")
    print("=" * 20)
    print(f"✅ Authentication: Working")
    print(f"✅ User Registration: Working")
    print(f"✅ Category Management: Working")
    print(f"✅ Ticket Creation: Working")
    print(f"{'✅' if comment_id else '❌'} Comment System: {'Working' if comment_id else 'Failed'}")
    print(f"{'✅' if vote_success else '❌'} Voting System: {'Working' if vote_success else 'Failed'}")
    print(f"{'✅' if status_update_success else '❌'} Status Updates: {'Working' if status_update_success else 'Failed'}")
    
    print(f"\n🎯 Created Resources:")
    print(f"   Demo Ticket ID: {ticket_id}")
    if comment_id:
        print(f"   Comment ID: {comment_id}")
    
    print(f"\n🌐 Access the web interface at: {BASE_URL}")
    print(f"   Admin login: {DEMO_ADMIN['email']} / {DEMO_ADMIN['password']}")
    print(f"   Test user: testuser@example.com / testpass123")

if __name__ == '__main__':
    main()