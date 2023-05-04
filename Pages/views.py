from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import CustomUser, Ticket, Service
from datetime import datetime
import speedtest
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
# Create your views here.

class HomeView(TemplateView):
    template_name= 'Pages/home.html'
    #extra_context = {'today': datetime.today()}

class ContactView(TemplateView):
    template_name= 'Pages/contact.html'

    def post(self, request):

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Send email using Django's built-in email sending functionality
        send_mail(
        subject,
        message,
        email,
        [settings.EMAIL_HOST_USER],
        fail_silently=False
        )

        # Redirect to a success page after the email is sent
        return HttpResponseRedirect(reverse(self.template_name))
        
    #return render(request, 'Pages/contact.html')


class AboutView(TemplateView):
    template_name= 'Pages/about.html'

class ServicesView(TemplateView):
    template_name= 'Pages/services.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name= 'Pages/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['full_name'] = f"{user.first_name} {user.last_name}"  # Concatenate the first name and last name
        return context



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
         # Authenticate the user using Django's built-in authenticate() function
        user = authenticate(request, username=username, password=password)

        # If the user is authenticated
        if user is not None:
            # Log the user in using Django's built-in login() function
            login(request, user)

            # retrieve the user type from the user object
            user_type = user.get_user_type()

            # Redirect the user to the appropriate page based on their user type
            if user_type == 'client':
                return redirect('dashboard')
            elif user_type == 'technician':
                return redirect('dashboard')
            elif user_type == 'admin':
                return redirect('dashboard')
        # If the user is not authenticated
        else:
            # Display an error message on the login page
            error_message = 'Invalid login credentials. Please try again.'
            return render(request, 'Pages/login.html', {'error_message': error_message})
    # If the request method is not POST
    else:
        return render(request, 'Pages/login.html')

    

def logout_view(request):
    logout(request)
    return redirect('login')

 

#Self Note: forms.py is used to define the structure and validation of HTML forms, while views.py is used to 
# define the logic for processing HTTP requests and generating HTTP responses. 
# Forms are used to capture user input and validate it, while views are used to handle the business logic and generate the 
# appropriate response based on the input received.
class CreateTicket(LoginRequiredMixin, CreateView):
    # Define the `Ticket` model that the view will create instances of
    model = Ticket
    # Define the fields of the `Ticket` model that the form will display and allow the user to input values for
    #fields = ['service','title', 'description']
    # Define the URL to redirect to after a successful form submission
    success_url = reverse_lazy('client_status')
    # Define the name of the HTML template file that will be used to render the view
    template_name = 'Pages/create_ticket.html'     

    class TicketForm(forms.ModelForm):
        service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label=None)           
        #price = forms.DecimalField(disabled=True, required=False)  # Add a readonly DecimalField for price

        class Meta:
            model = Ticket
            fields = ['service', 'title', 'phone', 'location', 'description']   

    form_class = TicketForm

    # Called upon succesful submission of form
    def form_valid(self, form):
        # Set the `client` field of the new `Ticket` instance to the logged-in user that submitted the form
        form.instance.client = self.request.user
        # Set the `status` field of the new `Ticket` instance to `'open'`
        form.instance.status = 'Open'
       
        # Call the `form_valid()` method of the superclass(add to the sql table) to handle the actual creation of the new `Ticket` instance
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Append the pre-filled line at the end of the existing description
        initial['description'] = f"{'-'*60}\n{self.request.user.username} - {self.request.user.user_type} at {current_time}:\n\n"
        return initial



class AdminTicketView(ListView):
    model = Ticket  # The model that the view displays
    template_name = 'Pages/admin_ticket.html'  # The template used to render the view
    context_object_name = 'tickets'  # The name of the variable used to store the queryset of objects

    # Handle POST requests to update ticket information
    def post(self, request):

        ticket_id = request.POST.get('ticket_id')  # Get ticket_id from POST data

        new_status = request.POST.get('new_status')  # Get new_status from POST data

        new_assignee_id = request.POST.get('new_assignee_id')  # Get new_assignee_id from POST data        

        if ticket_id and new_status:  # Check if ticket_id and new_status are not None
            # Get the ticket object to be updated
            ticket = Ticket.objects.get(id=ticket_id)

            if new_status in ['closed', 'Closed']:
                ticket.closed_at = datetime.now()
                
            ticket.status = new_status  # Update ticket status

            # If a new assignee is specified, update the assigned field
            if new_assignee_id:
                ticket.assigned = CustomUser.objects.get(id=new_assignee_id)
            
            if 'invoice' in request.FILES:
                ticket.invoice = request.FILES['invoice']           

            ticket.save()  # Save the updated ticket object
        return redirect('admin_ticket')  # Redirect to 'view_ticket' URL after updating ticket

    # Add additional context data to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Call the parent class's get_context_data method
        # Add the list of users to the context dictionary for use in the template
        context['users'] = CustomUser.objects.filter(user_type__in=['technician', 'admin'])
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()  # Call the parent class's get_queryset method

        status_filter = self.request.GET.get('status_filter')  # Get the value of status_filter from GET data

        # If status_filter is not None, filter the queryset based on the selected status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class TechnicianTicketView(ListView):
    model = Ticket  # The model that the view displays
    template_name = 'Pages/technician_ticket.html'  # The template used to render the view
    context_object_name = 'tickets'  # The name of the variable used to store the queryset of objects

    # Handle POST requests to update ticket information
    def post(self, request):
        ticket_id = request.POST.get('ticket_id')  # Get ticket_id from POST data
        new_status = request.POST.get('new_status')  # Get new_status from POST data
        new_assignee_id = request.POST.get('new_assignee_id')  # Get new_assignee_id from POST data
        if ticket_id and new_status:  # Check if ticket_id and new_status are not None
            # Get the ticket object to be updated
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = new_status  # Update ticket status
            # If a new assignee is specified, update the assigned field
            if new_assignee_id:
                ticket.assigned = CustomUser.objects.get(id=new_assignee_id)
            ticket.save()  # Save the updated ticket object
        return redirect('tech_ticket')  # Redirect to 'view_ticket' URL after updating ticket

    # Add additional context data to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Call the parent class's get_context_data method
        # Add the list of users to the context dictionary for use in the template
        context['users'] = CustomUser.objects.filter(user_type__in=['technician'])
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()  # Call the parent class's get_queryset method

        status_filter = self.request.GET.get('status_filter')  # Get the value of status_filter from GET data

        # Get the currently logged-in technician
        technician = self.request.user
        
        # Filter the queryset to only show tickets assigned to the current technician
        queryset = queryset.filter(assigned=technician)

        # If status_filter is not None, filter the queryset based on the selected status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class ClientTicketView(ListView):
    model = Ticket  # The model that the view displays
    template_name = 'Pages/view_status.html'  # The template used to render the view
    context_object_name = 'tickets'  # The name of the variable used to store the queryset of objects

    def get_queryset(self):
        # Filter the queryset based on the logged-in user
        queryset = super().get_queryset()
        queryset = queryset.filter(client_id=self.request.user.id)
        return queryset
    
class DeleteTicketView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'Pages/delete_ticket.html'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse('<script>window.opener.location.reload(); window.close();</script>')

class RateTechnicianView(UpdateView):
    model = Ticket
    template_name = 'Pages/rate_technician.html'
    fields = ['rating', 'rating_description']

    def form_valid(self, form):
        ticket = self.object        
        rating = self.request.POST.get('rating')
        rating_description = self.request.POST.get('rating_description')
        ticket.rating = rating
        ticket.rating_description = rating_description
        ticket.save()

        technician = ticket.assigned
        if technician:
            technician.performance = technician.get_average_rating()
            technician.save()
        return HttpResponse('<script>window.opener.location.reload(); window.close();</script>')
    

class TicketUpdateView(UpdateView):
    model = Ticket   
    fields = ['service', 'title', 'phone', 'description'] 
    template_name = 'Pages/ticket_update.html'
    success_url = reverse_lazy('dashboard')
    
    def get_initial(self):
        initial = super().get_initial()
        ticket = self.get_object()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Append the pre-filled line at the end of the existing description
        initial['description'] = f"{ticket.description}\n{'-'*60}\n{self.request.user.username} - {self.request.user.user_type} at {current_time}:\n\n"
        return initial
    


def speed_test(request):
    # Create a speedtest client
    st = speedtest.Speedtest()
    
    # Perform the speedtest
    st.get_best_server()
    download_speed = st.download() / 1000000 # convert to Mbps
    upload_speed = st.upload() / 1000000 # convert to Mbps
    
    # Round the speeds to two decimal places
    download_speed = round(download_speed, 2)
    upload_speed = round(upload_speed, 2)

    # Render the results in a template
    context = {
        'download_speed': download_speed,
        'upload_speed': upload_speed,
    }
    return render(request, 'Pages\dashboard.html', context)
