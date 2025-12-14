from principal.models import Genero
from django import forms
   
class BusquedaPorGeneroForm(forms.Form):
    genero = forms.ModelChoiceField(label="Seleccione el género", queryset=Genero.objects.all())
    
class BusquedaPorFechaForm(forms.Form):
    fecha = forms.DateField(label="Fecha (Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'))