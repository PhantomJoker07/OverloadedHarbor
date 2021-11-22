# Overloaded Harbor 
## Proyecto de Simulación, 2021
### `Gabriel Fernando Martín Fernández C-411`

## Problema (Overloaded Harbor)

En un puerto de supertanqueros que cuenta con 3 muelles y un remolcador
para la descarga de estos barcos de manera simultánea se desea conocer el tiempo
promedio de espera de los barcos para ser cargados en el puerto.

El puerto cuenta con un bote remolcador disponible para asistir a los tanqueros. Los tanqueros de cualquier tamaño necesitan de un remolcador para
aproximarse al muelle desde el puerto y para dejar el muelle de vuelta al puerto.

El tiempo de intervalo de arribo de cada barco distribuye mediante una función exponencial
con $\lambda = 8$ horas. Existen tres tamaños distintos de tanqueros:
pequeño, mediano y grande, la probabilidad correspondiente al tamaño de cada
tanquero se describe en la tabla siguiente. El tiempo de carga de cada tanquero
depende de su tamaño y los parámetros de distribución normal que lo representa
también se describen en la tabla siguiente.

| Tamaño  | Probabilidad de Arribo | Tiempo de Carga          |
| ---     | ---                    | ---                      |
| Pequeño | 0.25                   | $\mu = 9, \sigma^2 = 1$  |
| Mediano | 0.25                   | $\mu = 12, \sigma^2 = 2$ |
| Grande  | 0.5                    | $\mu = 18, \sigma^2 = 3$ |

De manera general, cuando un tanquero llega al puerto, espera en una cola
(virtual) hasta que exista un muelle vacío y que un remolcador esté disponible
para atenderle. Cuando el remolcador está disponible lo asiste para que pueda
comenzar su carga, este proceso demora un tiempo que distribuye exponencial
con $\lambda = 2$ horas. El proceso de carga comienza inmediatamente después de que
el barco llega al muelle. Una vez terminado este proceso es necesaria la asistencia
del remolcador (esperando hasta que esté disponible) para llevarlo de vuelta al
puerto, el tiempo de esta operación distribuye de manera exponencial con $\lambda = 1$
hora. El traslado entre el puerto y un muelle por el remolcador sin tanquero
distribuye exponencial con $\lambda = 15$ minutos.

Cuando el remolcador termina la operación de aproximar un tanquero al
muelle, entonces lleva al puerto al primer barco que esperaba por salir, en caso de
que no exista barco por salir y algún muelle esté vacío, entonces el remolcador se
dirige hacia el puerto para llevar al primer barco en espera hacia el muelle vacío;
en caso de que no espere ningún barco, entonces el remolcador esperará por algún barco en un muelle para llevarlo al puerto. Cuando el remolcador termina
la operación de llevar algún barco al puerto, este inmediatamente lleva al primer
barco esperando hacia el muelle vacío. En caso de que no haya barcos en los
muelles, ni barcos en espera para ir al muelle, entonces el remolcador se queda
en el puerto esperando por algún barco para llevar a un muelle.

Simule completamente el funcionamiento del puerto. Determine el tiempo
promedio de espera en los muelles.

## Ideas Generales

Podemos definir dos actores principales en este problema: los barcos y el remolcador, el estado de ambos define el comportamiento futuro que tendrá la simulación que deseamos realizar. Esta simulación abarca un período que puede extenderse por varias horas sin embargo durante la mayor parte del tiempo tanto el remolcador como los barcos se encuentran realizando una actividad dada y no hay cambios en sus estados. Por tanto lo primero fue definir cuáles momentos nos interesaba analizar determinando cuando ocurre un cambio en el estado de las entidades involucradas. Señalamos 3 tipos de eventos que cambian el estado de la simulación:
- Arriba un nuevo barco al puerto
- El remolcador llega al puerto/muelle tras un viaje
- Un barco finaliza el proceso de carga

Estos 3 tipos eventos nos sirven perfectamente para generar al resto pues el primero genera eventos del segundo tipo, el segundo tipo genera eventos de su mismo tipo y del tercer tipo, mientras que el tercer tipo genera eventos del segundo tipo solamente. El comienzo del proceso de carga de un barco o la salida del barco del muelle/puerto se asume que ocurren de manera instantánea luego de uno de estos 3 tipos de eventos y por ello no se tienen en cuenta como desencadenates de cambios.

Se tienen en cuenta varios estados que describen la situación de la simulación, como ya se mencionó los cambios en estos estados solo son provocados por los eventos descritos. Los posibles estados del remolcador son:
- Esperando en el muelle
- Esperando en el puerto
- De camino al Puerto
- De camino al Muelle

En el caso de los barcos notemos que la mayoría de sus estados vienen ligados al estado del remolcador por lo que si llevamos una relación de que barco escolta el remolcador estos pasan a simplificarse y solo tenemos que saber si el barco esta esperando en el puerto o si terminó el proceso de carga. Además el hecho de saber cuando se terminó el proceso de carga se le puede asociar al estado del propio muelle donde este está cargando y su estado de espera se puede asociar al puerto. Por tanto tenemos que lejos de llevar el estado de cada barco podemos llevar el estado del puerto y de los muelles sin perder información. De esta manera establecemos una cola en el puerto y en los muelles donde registramos la información de los barcos y cuando un barco se encuentra viajando está asociado al remolcador. De manera general nos interesará saber del puerto cuando llega un barco o cuando esté vacío y del muelle cuando está vacío, lleno, tiene un lugar libre o contiene un barco que termino de cargar.

Para facilitar la consulta de los estados se agragaron varios elementos auxiliares para describir la información como por ejemplo un diccionario que registra los barcos que están actualmente en la simulación y no han terminado sus procesos, listas para describir los estados de los muelles junto con una cola de prioridad para atender a los barcos que terminan de salir. Y como no podia faltar: un listado de los tiempos de espera que se actualiza cada vez que el remolcador recoge un barco en el muelle luego de que este termine de cargar y nos sirve de contador. 

Todas las variables usadas para la simulación tienen una breve descripción de su uso en su declaración en la clase Overload_Harbor


## Modelo de Simulación

Teniendo en cuenta las ideas antes descritas podemos decir que nuestro modelo se basa en el de 2 servidores en serie. En este caso el remolcador será como el primer servidor y el muelle será el segundo. Consideramos aquí el conjunto de los muelles como una sola entidad. La particularidad de este modelo es que luego de pasar del primer servidor al segundo se vuelve a regresar al primero. El cliente en este caso sería el barco.


## Resultados

El tiempo media de espera en los muelles que se obtuvo fue de alrededor de 15 horas. A continuación presentaremos algunos detalles interesantes al respecto y efectos que tiene el cambio de parámetros en la solución del problema. Los tiempos dados en la tablas se refieren a horas.

Un detalle importante de la implementación del problema es la forma en la que se generan las variables que siguen distribución normal debido a que el inverso de la equación de dicha distribución no está bien definido. Una forma de buscar una aproximación a esta función es usar por ejemplo series de Taylor pero también existe un método más rápido con cierta fidelidad: Box-Muller. En este caso presentamos la diferencia en el resultado que obtenemos al usar dicho método o el implementado en la librería de scipy.

| Método usado para generar la distribución normal | Tiempo medio de espera en el muelle |
| ---                                              | ---                                 |
| usando scipy.norm                                | 14.98                               |
| Box-Muller                                       | 15.44                               |

El método de scipy es más exacto sin embargo también es más lento por lo que cada uno de los métodos es preferible en distintas circunstancias según que se quiera optimizar. En este caso como disponemos de tiempo para realizar la simulación mostraremos de aquí en adelante solo los resultados usando scipy.norm.

Segun la distribucion que sigue el tiempo de carga, los barcos pequeños tienen media 9h con probabilidad 0.25, los medianos, media 12 con probabilidad 0.25 y los grandes media 18 con probabilidad 0.5. Esto quiere decir que en promedio llegan n barcos grandes, n/2 barcos pequeños y n/2 barcos medianos. Esto da una media de tiempo de carga de (9n/2+12n/2+18n)/(2n)=28.5/2=14.25 horas. Esto sería la media esperada del tiempo de carga si siempre hubiese un remolcador disponible en cuanto un barco termina de cargar. Vemos que por tanto la diferencia de lo obtenido respecto a este valor recae en el tiempo que demora el remolcador en estar disponible lo cual a su vez está infuido por los tiempos de viaje. Además si por ejemplo aumentáramos el número de muelles sería más probable que un barco terminase y el remolcador estuviese ocupado, este efecto lo podemos ver en la siguente tabla:


| Muelles | Tiempo medio de espera en el muelle |
| ---     | ---                                 |
| 3       | 14.98                               |
| 5       | 15.28                               |
| 10      | 15.31                               |

Si por ejemplo reducimos el valor medio de los tiempos de viaje en un factor de 10 el valor medio de espera daría alrededor de 14.27 horas, bastante cercano a la media si el remolcador estuviese siempre disponible. Si por lo contrario aumentamos el valor medio de los tiempos de viaje en un factor de 10 la influencia de estos viajes es tal que la media de espera sube a 59.84 horas.
 
## Ejecución

Para ejecutar con los valores por defecto

```bash
python main.py
```

Se pueden alterar los parámetros de entrada modificando propiedades de la instancia de la clase Overloaded_Harbor desde main.py antes de ejecutar el método run() de esta clase. Por ejemplo:

```bash
    test = Overloaded_Harbor()
    test.dock_count = 4   # Cambia la cantidad de muelles a 4
    test.run(100)
```