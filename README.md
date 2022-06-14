PAV - P5: síntesis musical polifónica
=====================================

Obtenga su copia del repositorio de la práctica accediendo a [Práctica 5](https://github.com/albino-pav/P5) 
y pulsando sobre el botón `Fork` situado en la esquina superior derecha. A continuación, siga las
instrucciones de la [Práctica 2](https://github.com/albino-pav/P2) para crear una rama con el apellido de
los integrantes del grupo de prácticas, dar de alta al resto de integrantes como colaboradores del proyecto
y crear la copias locales del repositorio.

Como entrega deberá realizar un *pull request* con el contenido de su copia del repositorio. Recuerde que
los ficheros entregados deberán estar en condiciones de ser ejecutados con sólo ejecutar:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.sh
  make release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A modo de memoria de la práctica, complete, en este mismo documento y usando el formato *markdown*, los
ejercicios indicados.

Ejercicios.
-----------

### Envolvente ADSR.

Tomando como modelo un instrumento sencillo (puede usar el InstrumentDumb), genere cuatro instrumentos que
permitan visualizar el funcionamiento de la curva ADSR.

El fichero de los que contiene los instrumentos mostrados a continuación es [dumb.orc](work/dumb.orc).

* Un instrumento con una envolvente ADSR genérica, para el que se aprecie con claridad cada uno de sus
  parámetros: ataque (A), caída (D), mantenimiento (S) y liberación (R).

    ```text
    # Generic ADSR
    1	InstrumentDumb	ADSR_A=0.20; ADSR_D=0.10; ADSR_S=0.20; ADSR_R=0.30; N=16;
    ```
    ![Generic](img/generic-adsr.png)

* Un instrumento *percusivo*, como una guitarra o un piano, en el que el sonido tenga un ataque rápido, no
  haya mantenimiemto y el sonido se apague lentamente.
  - Para un instrumento de este tipo, tenemos dos situaciones posibles:
    * El intérprete mantiene la nota *pulsada* hasta su completa extinción.

    ```text
    # Percusive 1 ADSR
    2	InstrumentDumb	ADSR_A=0.01; ADSR_D=0.20; ADSR_S=0.00; ADSR_R=0.00; N=127;
    ```
    ![Percusive 1](img/percusive1-adsr.png)


    * El intérprete da por finalizada la nota antes de su completa extinción, iniciándose una disminución
	  abrupta del sonido hasta su finalización.
    
    ```text
    # Percusive 2 ADSR
    3	InstrumentDumb	ADSR_A=0.01; ADSR_D=0.20; ADSR_S=0.00; ADSR_R=0.01; N=127;
    ```
    ![Percusive 2](img/percusive2-adsr.png)

  - Debera representar en esta memoria **ambos** posibles finales de la nota.

* Un instrumento *plano*, como los de cuerdas frotadas (violines y semejantes) o algunos de viento. En
  ellos, el ataque es relativamente rápido hasta alcanzar el nivel de mantenimiento (sin sobrecarga), y la
  liberación también es bastante rápida.

    ```text
    # Plain ADSR
    4	InstrumentDumb	ADSR_A=0.05; ADSR_D=0.00; ADSR_S=0.40; ADSR_R=0.60; N=92;
    ```
    ![Plain](img/plain-adsr.png)

Para los cuatro casos, deberá incluir una gráfica en la que se visualice claramente la curva ADSR. Deberá
añadir la información necesaria para su correcta interpretación, aunque esa información puede reducirse a
colocar etiquetas y títulos adecuados en la propia gráfica (se valorará positivamente esta alternativa).


*Nota:* Ficheros generados para este ejercicio:
-   [Instrumentos (.orc)](work/adsr.orc)
-   [Partitura (.sco)](work/adsr.sco)
-   [Audio (.wav)](work/adsr.wav)

### Instrumentos Dumb y Seno.

Implemente el instrumento `Seno` tomando como modelo el `InstrumentDumb`. La señal **deberá** formarse
mediante búsqueda de los valores en una tabla.

- Incluya, a continuación, el código del fichero `seno.cpp` con los métodos de la clase Seno.
  ```cpp
  #include <iostream>
  #include <math.h>
  #include "seno.h"
  #include "keyvalue.h"
  
  #include <stdlib.h>
  
  using namespace upc;
  using namespace std;
  
  Seno::Seno(const std::string &param) 
    : adsr(SamplingRate, param) {
    bActive = false;
    x.resize(BSIZE);
  
    KeyValue kv(param);
  
    if (!kv.to_int("N", N)) {
      N = 40; //default value
    }
  
    //Create a tbl with one period of a sinusoidal wave
    tbl.resize(N);
    float phase = 0, step = 2 * M_PI /(float) N;
    index = 0.0f;
  
    for (int i=0; i < N ; ++i) {
      tbl[i] = sin(phase);
      phase += step;
    }
  }
  
  
  void Seno::command(long cmd, long note, long vel) {
    if (cmd == 9) {		//'Key' pressed: attack begins
      bActive = true;
      adsr.start();
      index = 0;
  
      if (vel > 127) {
          vel = 127;
      }
      A = vel / 127.0f;
  
      // Calculate delta for the table index
      float f0_note = 440 * powf(2, (note - 69.0f) / 12.0f);
      delta_idx = (float)N * f0_note / SamplingRate;
      
    } else if (cmd == 8) {	//'Key' released: sustain ends, release begins
      adsr.stop();
  
    } else if (cmd == 0) {	//Sound extinguished without waiting for release to end
      adsr.end();
    }
  }
  
  
  const vector<float> & Seno::synthesize() {
    if (not adsr.active()) {
      x.assign(x.size(), 0);
      bActive = false;
      return x;
  
    } else if (not bActive) {
      return x;
    }
  
    float frac;
    int il, ir;
  
    for (unsigned int i = 0; i < x.size(); ++i, index += delta_idx) {
      // Check out of bounds
      if (index > (float)tbl.size()) {
          index -= (float) tbl.size();
      }
  
      // Get base and fraction indices
      il = (int)floor(index);
      frac = index - (float)il;
  
      // See if left index is last sample or not
      ir = il + 1;
      if (il == (int)tbl.size() - 1) {
        ir = 0;
        index -= tbl.size();
      }
  
      // Lerp
      x[i] = A * ((1-frac)*tbl[il] + frac*tbl[ir]);
    
      // Uncomment to get data to plot
      // printf("%.10f\t%.10f\t%.10f\n", tbl[il], tbl[ir], ((1-frac)*tbl[il] + frac*tbl[ir]));
    }
  
    //apply envelope to x and update internal status of ADSR
    adsr(x);
  
    return x;
  }
  ```

- Explique qué método se ha seguido para asignar un valor a la señal a partir de los contenidos en la tabla,
  e incluya una gráfica en la que se vean claramente (use pelotitas en lugar de líneas) los valores de la
  tabla y los de la señal generada.

  El primer paso es calcular el tono de la nota, en hercios, a partir de su valor en semitonos. Esto se hace
  a partir de la formula dada en el enunciado:
  ```cpp
  float f0_note = 440 * powf(2, (note - 69.0f) / 12.0f);
  ```

  Una vez se tiene el tono se debe calcular el avance del indice con la siguiente fórmula:
  ```cpp
  delta_idx = (float)N * f0_note / SamplingRate;
  ```

  Como esta delta seguramente no sera un valor entero se tendran indices no enteros, para solucionar esto hay
  dos maneras:
    - Redondear: La mas fácil de implementar. (**No implementado**)
    - Interpolación lineal, que es por la que he optado. En este caso se usa la parte decimal del indice
      como peso.
  
  *Nota:* A la hora de interpolar puede que se tenga que hacer entre la última y primera muestra.

  En la siguiente imagen se pueden ver los valores de la tabla y los valores interpolados:

  ![Table interpolation](img/table-interpolation.png)
    
- Si ha implementado la síntesis por tabla almacenada en fichero externo, incluya a continuación el código
  del método `command()`.

  **TODO**

*Nota:* Ficheros usados para este ejercicio:
-   [Instrumentos (.orc)](work/seno.orc)
-   [Partitura (.sco)](work/doremi.sco)
-   [Audio (.wav)](work/doremi.wav)
-   [Generar gráfica](scripts/plot-interpolation.py)

### Efectos sonoros.

- Incluya dos gráficas en las que se vean, claramente, el efecto del trémolo y el vibrato sobre una señal
  sinusoidal. Deberá explicar detalladamente cómo se manifiestan los parámetros del efecto (frecuencia e
  índice de modulación) en la señal generada (se valorará que la explicación esté contenida en las propias
  gráficas, sin necesidad de *literatura*).
- Si ha generado algún efecto por su cuenta, explique en qué consiste, cómo lo ha implementado y qué
  resultado ha producido. Incluya, en el directorio `work/ejemplos`, los ficheros necesarios para apreciar
  el efecto, e indique, a continuación, la orden necesaria para generar los ficheros de audio usando el
  programa `synth`.

### Síntesis FM.

Construya un instrumento de síntesis FM, según las explicaciones contenidas en el enunciado y el artículo
de [John M. Chowning](https://web.eecs.umich.edu/~fessler/course/100/misc/chowning-73-tso.pdf). El
instrumento usará como parámetros **básicos** los números `N1` y `N2`, y el índice de modulación `I`, que
deberá venir expresado en semitonos.

- Use el instrumento para generar un vibrato de *parámetros razonables* e incluya una gráfica en la que se
  vea, claramente, la correspondencia entre los valores `N1`, `N2` e `I` con la señal obtenida.
- Use el instrumento para generar un sonido tipo clarinete y otro tipo campana. Tome los parámetros del
  sonido (N1, N2 e I) y de la envolvente ADSR del citado artículo. Con estos sonidos, genere sendas escalas
  diatónicas (fichero `doremi.sco`) y ponga el resultado en los ficheros `work/doremi/clarinete.wav` y
  `work/doremi/campana.work`.
  * También puede colgar en el directorio work/doremi otras escalas usando sonidos *interesantes*. Por
    ejemplo, violines, pianos, percusiones, espadas láser de la
	[Guerra de las Galaxias](https://www.starwars.com/), etc.

### Orquestación usando el programa synth.

Use el programa `synth` para generar canciones a partir de su partitura MIDI. Como mínimo, deberá incluir la
*orquestación* de la canción *You've got a friend in me* (fichero `ToyStory_A_Friend_in_me.sco`) del genial
[Randy Newman](https://open.spotify.com/artist/3HQyFCFFfJO3KKBlUfZsyW/about).

- En este triste arreglo, la pista 1 corresponde al instrumento solista (puede ser un piano, flautas,
  violines, etc.), y la 2 al bajo (bajo eléctrico, contrabajo, tuba, etc.).
- Coloque el resultado, junto con los ficheros necesarios para generarlo, en el directorio `work/music`.
- Indique, a continuación, la orden necesaria para generar la señal (suponiendo que todos los archivos
  necesarios están en directorio indicado).

También puede orquestar otros temas más complejos, como la banda sonora de *Hawaii5-0* o el villacinco de
John Lennon *Happy Xmas (War Is Over)* (fichero `The_Christmas_Song_Lennon.sco`), o cualquier otra canción
de su agrado o composición. Se valorará la riqueza instrumental, su modelado y el resultado final.
- Coloque los ficheros generados, junto a sus ficheros `score`, `instruments` y `efffects`, en el directorio
  `work/music`.
- Indique, a continuación, la orden necesaria para generar cada una de las señales usando los distintos
  ficheros.
