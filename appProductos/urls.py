from django.urls import path 
from . import views 

urlpatterns = [ 
     path('categorias/', views.verCategorias, name='categorias'),
     path('productos/<str:idCategoria>', views.verProductosCategoria, name='productos'), 
     path('producto/<str:idProd>', views.verProducto, name='un_producto'),
     path('carro/<str:idProd>', views.agregarCarro, name='agregarCarro'), 
     path('carrito/', views.verCarrito, name='carrito'), 
     path('eliminar/<str:id>', views.eliminarCarrito, name='eliminar'),
     path('cambiarCantidad/', views.cambiarCantidad),
     path('pagar/', views.pagarCarrito, name='pagar'),
]