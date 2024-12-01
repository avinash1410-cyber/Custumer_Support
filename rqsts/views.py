from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from .models import Customer, Request, Support  # Ensure Support is imported
from django.contrib.auth.decorators import login_required



from django.contrib.auth import logout,login,authenticate
from django.http import JsonResponse

def user_logout(request):
    """
    Logs out the currently logged-in user.
    """
    logout(request)
    return JsonResponse({'message': 'Logout successful.'}, status=200)





def user_login(request):
    """
    Logs in a user via a POST request with username and password.
    """
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Extract username and password from the request body
            username = data.get('username')
            password = data.get('password')

            # Validate the credentials
            if not username or not password:
                return JsonResponse({'error': 'Username and password are required.'}, status=400)

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(request, user)

                return JsonResponse({'message': 'Login successful.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)





@login_required
def view_profile(request):
    """
    Allows a user to view their profile details.
    """
    try:
        # Fetch the customer associated with the logged-in user
        customer = Customer.objects.get(user=request.user)

        # Prepare the response data
        data = {
            "username": request.user.username,
            "email": customer.email,
            "profile_created_at": customer.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse(data, status=200)

    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Profile not found.'}, status=404)







@csrf_exempt
def create_request(request):
    """
    Allows a customer to create a Request via POST request.
    """
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Get the associated customer
            user_id = data.get('user_id')
            customer = get_object_or_404(Customer, user_id=user_id)

            # Extract fields for the Request
            text = data.get('text')
            email = data.get('email', customer.email)  # Default to the customer's email if not provided

            # Validate required fields
            if not text:
                return JsonResponse({'error': 'Text field is required.'}, status=400)

            # Create the Request
            rqst = Request.objects.create(
                user=customer,
                text=text,
                email=email,
                status='PENDING',  # Default status for new requests
                created_at=now()
            )

            return JsonResponse({
                'message': 'Request created successfully.',
                'request_id': rqst.id,
                'status': rqst.status,
                'created_at': rqst.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)

def start_working_on_request(request, rqst_id):
    """
    Mark a request as 'IN_PROGRESS' to indicate work has started.
    """
    if not Support.objects.filter(user=request.user).exists():
        return JsonResponse({'error': 'You do not have permission to work on this request.'}, status=403)

    if request.method == "POST":
        try:
            # Fetch the request object
            rqst = get_object_or_404(Request, id=rqst_id)

            # Check if the request is already in progress or resolved
            if rqst.status == 'IN_PROGRESS':
                return JsonResponse({'error': 'Request is already in progress.'}, status=400)
            if rqst.status == 'RESOLVED':
                return JsonResponse({'error': 'Cannot start work on a resolved request.'}, status=400)

            # Update the status to 'IN_PROGRESS' and set the start time
            rqst.status = 'IN_PROGRESS'
            rqst.started_at = now()  # Add a started_at timestamp if your model supports it
            rqst.save()

            return JsonResponse({
                'message': f'Request {rqst_id} marked as "IN_PROGRESS".',
                'status': rqst.status,
                'started_at': rqst.started_at.strftime('%Y-%m-%d %H:%M:%S') if rqst.started_at else None
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)

def show_request_details(request, rqst_id):
    """
    Display the details of a specific request, including its current status and other details.
    """
    if request.method == "GET":
        try:
            # Fetch the request object
            rqst = get_object_or_404(Request, id=rqst_id)

            if not (rqst.user.user == request.user or Support.objects.filter(user=request.user).exists()):
                return JsonResponse({'error': 'You do not have permission to view this request.'}, status=403)

            # Prepare the response data
            data = {
                "id": rqst.id,
                "user": rqst.user.user.username,  # Assuming user is linked to a Customer with a User object
                "text": rqst.text,
                "email": rqst.email,
                "status": rqst.status,
                "created_at": rqst.created_at.strftime('%Y-%m-%d %H:%M:%S') if rqst.created_at else None,
                "resolved_at": rqst.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if rqst.resolved_at else None,
            }

            return JsonResponse(data, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Use GET.'}, status=405)
