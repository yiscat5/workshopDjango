from django.shortcuts import render 
from .models import * 
from django.template.loader import render_to_string 
from django.core.mail import EmailMessage

# Create your views here. 
def verCategorias(request): 
     #Consultar categorias 
     listaCateg = Categoria.objects.all() 
     
     #ensamblar context 
     
     context = {
          'categorias': listaCateg, 
          'titulo': 'Categorias de Productos del Supermercado', 
     } 
          
     #renderizar 
     return render(request, 'productos/categorias.html', context)

# Create your views here.

def verProductosCategoria(request, idCategoria): 
     #Consultar categorias 
     idCat = int(idCategoria) 
     nombreCat = Categoria.objects.get(id=idCat)
     listaProductos = Producto.objects.filter(categoria= idCat) 
     
     #ensamblar context 
     context = { 
          'productos': listaProductos, 
          'titulo': 'Productos de la categoria ' + str(nombreCat), } 
          
     #renderizar 
     return render(request, 'productos/productos.html', context)

def verProducto(request, idProd, msj = None): 
     #Consultar 
     idProd = int(idProd) 
     regProducto = Producto.objects.get(id= idProd) 
     #ensamblar context 
     context = { 
          'producto': regProducto, 
          'titulo': 'Detalles de ' + str(regProducto.nombre), 
     } 
          
     if msj: 
          context['mensaje']= msj 
     #renderizar 
     return render(request, 'productos/producto.html', context)

def agregarCarro(request, idProd): 
     idProd = int(idProd) 
     regUsuario = request.user 
     msj = None 
     #leer reg del producto en Producto 
     existe = Producto.objects.filter(id=idProd).exists() 
     if existe: 
          regProducto = Producto.objects.get(id=idProd) 
          
          # si no existe en carrito: 
          existe = Carro.objects.filter(producto=regProducto, estado= 'activo', usuario= 
regUsuario).exists() 
          if existe: 
               # instanciar un objeto de la clase Carrito 
               regCarro = Carro.objects.get(producto=regProducto, estado= 'activo', usuario= regUsuario) 
               #incrementar cantidad 
               regCarro.cantidad += 1 
          else: 
               regCarro = Carro(producto=regProducto, usuario= regUsuario, valUnit = 
regProducto.precioUnitario) 

          # guardar el registro 
          regCarro.save() 
     else: 
          # dar mensaje 
          msj = 'Producto no disponible' 
          # redireccionar a 'verProducto' 
     return verProducto(request, idProd, msj)

def verCarrito(request): 
     context = consultarCarro(request) 
     return render(request, 'productos/carrito.html', context)

def eliminarCarrito(request, id): 
     #Consultar el reg y cambiar estado 
     regCarrito = Carro.objects.get(id=id) 
     regCarrito.estado = 'anulado' 
     #guardar en BD 
     regCarrito.save() 
     #Desplegar el carrito 
     return verCarrito(request)

def cambiarCantidad(request): 
     is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 
     if is_ajax: 
          if request.method == 'POST': 
               #Toma la data enviada por el cliente 
               data = json.load(request) 
               id = data.get('id') 
               cantidad = int(data.get('cantidad')) 
               if cantidad > 0: 
                    #Lee el registro y lo modifica 
                    regProducto = Carro.objects.get(id=id) 
                    regProducto.cantidad = cantidad 
                    regProducto.save() 
               context = consultarCarro(request) 
               return JsonResponse(context) 
          return JsonResponse({'alarma': 'no se pudo modificar...'}, status=400) 
     else: 
          return verCarrito(request)

def consultarCarro(request): 
     #get usuario 
     regUsuario = request.user 
     #filtrar productos de ese usuario en estado 'activo' 
     listaCarrito = Carro.objects.filter(usuario= regUsuario, estado= 'activo').values('id', 
'cantidad', 'valUnit', 'producto__imgPeque', 'producto__nombre','producto__unidad', 'producto__id') 
     #renderizar 
     listado = [] 
     subtotal = 0 
     for prod in listaCarrito: 
          reg = {
               'id': prod['id'], 
               'cantidad': prod['cantidad'],
               'valUnit': prod['valUnit'], 
               'imgPeque': prod['producto__imgPeque'], 
               'nombre': prod['producto__nombre'], 
               'unidad': prod['producto__unidad'], 
               'total': prod['valUnit'] * prod['cantidad'], 
               'prodId': prod['producto__id'], 
          } 
          subtotal += prod['valUnit'] * prod['cantidad'] 
          
          listado.append(reg)
     envio = 8000 
     if len(listado) == 0: 
          envio = 0 
     
     context = { 
          'titulo': 'Productos en el carrito de compras', 
          'carrito': listado, 
          'subtotal': subtotal, 
          'iva': int(subtotal) * 0.19, 
          'envio': envio, 
          'total': int(subtotal) * 1.19 + envio 
     } 
     
     return context

def pagarCarrito(request): 
     context = consultarCarro(request) 
     regUsuario = request.user 
     nombreUsuario = str(regUsuario) 
     context['nombre'] = nombreUsuario 
     correo = regUsuario.email 
     
     #--- MODULO PARA ENVIO DE CORREO 
     mail_subject = 'Factura de compra' 
     body = render_to_string('productos/html_email.html', context) 
     to_email = [correo] #Lista con el o los correos de destino 
     
     send_email = EmailMessage(mail_subject, body, to= to_email ) 
     send_email.content_subtype = 'html' 
     send_email.send() 
     #---FIN MODULO PARA ENVIO DE CORREO DE CONFIRMACION 
     
     # sacar productos del carrito 
     listaCarrito = Carro.objects.filter(usuario= regUsuario, estado= 'activo') 
     for regCarro in listaCarrito: 
          regCarro.estado = 'comprado' 
          regCarro.save() 
          
     #redireccionar 
     return verCategorias(request)