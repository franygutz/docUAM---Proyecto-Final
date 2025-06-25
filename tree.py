class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

class ArbolBinario:
    def __init__(self):
        self.raiz = None
    
    def insertar(self, nodo):
        if self.raiz is None:
            self.raiz = nodo
        else:
            self._insertar_recursivo(self.raiz, nodo)
    
    def _insertar_recursivo(self, nodoActual, nodo):
        if nodo.valor < nodoActual.valor:
            # Insertamos en el subárbol izquierdo
            if nodoActual.izquierda is None:
                nodoActual.izquierda = nodo
            else:
                self._insertar_recursivo(nodoActual.izquierda, nodo)
        elif nodo.valor > nodoActual.valor:
            # Insertamos en el subárbol derecho
            if nodoActual.derecha is None:
                nodoActual.derecha = nodo
            else:
                self._insertar_recursivo(nodoActual.derecha, nodo)
        else:  # Si el valor es igual, lo insertamos en el subárbol izquierdo
            if nodoActual.izquierda is None:
                nodoActual.izquierda = nodo
            else:
                self._insertar_recursivo(nodoActual.izquierda, nodo)

    def inorden(self):
        sorted_docs = []
        self._inorden_recursivo(self.raiz, sorted_docs)
        return sorted_docs
    
    def _inorden_recursivo(self, nodo, sorted_docs):
        if nodo is not None:
            self._inorden_recursivo(nodo.izquierda, sorted_docs)
            sorted_docs.append(nodo.valor.document)
            self._inorden_recursivo(nodo.derecha, sorted_docs)

    def preorden(self):
        self._preorden_recursivo(self.raiz)
        print()
    
    def _preorden_recursivo(self, nodo):
        if nodo is not None:
            print(nodo.valor, end=' ')
            self._preorden_recursivo(nodo.izquierda)
            self._preorden_recursivo(nodo.derecha)

    def postorden(self):
        self._postorden_recursivo(self.raiz)
        print()
    
    def _postorden_recursivo(self, nodo):
        if nodo is not None:
            self._postorden_recursivo(nodo.izquierda)
            self._postorden_recursivo(nodo.derecha)
            print(nodo.valor, end=' ')