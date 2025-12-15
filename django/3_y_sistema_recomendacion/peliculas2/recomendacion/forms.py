from django import forms

class PeliculaBusquedaForm(forms.Form):
    idPelicula = forms.CharField(label="Id de Pelicula", widget=forms.TextInput, required=True)