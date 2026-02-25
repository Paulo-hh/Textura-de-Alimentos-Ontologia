import tkinter as tk
from tkinter import ttk, messagebox
from rdflib import Graph, RDF, RDFS, OWL, Namespace

class OntologiaDinamica:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualização dos Dados da Ontologia - Textura de Alimentos")
        self.root.geometry("850x550")

        self.g = Graph()
        try:
            caminho = r"C:\Projetos\Trabalho WSO\Textura de Alimentos.rdf" # mudar caminho
            self.g.parse(caminho, format="xml")
            print("Ontologia carregada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {e}")

        self.setup_ui()
        self.popular_classes()

    def setup_ui(self):
        # Container principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Frame de filtros
        frame_filtros = tk.LabelFrame(main_frame, text=" Filtros de Busca ", padx=10, pady=10)
        frame_filtros.pack(fill="x", pady=(0, 15))

        # 1. Menu de Classes (Corrigido: padx ao invés de px)
        tk.Label(frame_filtros, text="Classe:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_classes = ttk.Combobox(frame_filtros, width=45, state="readonly")
        self.cb_classes.grid(row=0, column=1, padx=5, pady=5)
        
        # 2. Botão de Busca
        self.btn_buscar = tk.Button(frame_filtros, text="🔍 Buscar Instâncias", 
                                   command=self.listar_instancias, bg="#4CAF50", fg="white", padx=10)
        self.btn_buscar.grid(row=0, column=2, padx=10, pady=5)

        # Tabela de Resultados
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        self.tree = ttk.Treeview(main_frame, columns=("Instancia", "Propriedade", "Valor"), show='headings')
        self.tree.heading("Instancia", text="Instancias ")
        self.tree.heading("Propriedade", text="Relação ")
        self.tree.heading("Valor", text="Valor")
        
        # Ajuste de largura das colunas
        self.tree.column("Instancia", width=200)
        self.tree.column("Propriedade", width=150)
        self.tree.column("Valor", width=350)
        
        self.tree.pack(expand=True, fill='both')

    def popular_classes(self):
        """Extrai classes da ontologia de forma robusta"""
        classes = []
        for s in self.g.subjects(RDF.type, OWL.Class):
            nome = self.limpar_uri(s)
            if nome: classes.append(nome)
        
        for s in self.g.subjects(RDF.type, RDFS.Class):
            nome = self.limpar_uri(s)
            if nome and nome not in classes: classes.append(nome)
        
        self.cb_classes['values'] = sorted(classes)
        if classes:
            self.cb_classes.current(0)

    def limpar_uri(self, uri):
        """Remove a URL longa e retorna apenas o nome após o # ou /"""
        uri_str = str(uri)
        if "#" in uri_str:
            return uri_str.split("#")[-1]
        return uri_str.split("/")[-1]

    def listar_instancias(self):
        """Busca instâncias e suas propriedades baseadas na classe selecionada"""
        classe_sel = self.cb_classes.get()
        if not classe_sel:
            return

        for i in self.tree.get_children(): 
            self.tree.delete(i)

        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?instancia ?p ?o WHERE {{
            ?instancia rdf:type ?tipo .
            ?instancia ?p ?o .
            FILTER(CONTAINS(STR(?tipo), "{classe_sel}")) .
            FILTER(?p != rdf:type) .
        }}
        """
        
        try:
            results = self.g.query(query)
            count = 0
            for row in results:
                inst = self.limpar_uri(row.instancia)
                pred = self.limpar_uri(row.p)
                obj = self.limpar_uri(row.o)
                self.tree.insert("", tk.END, values=(inst, pred, obj))
                count += 1
            
            if count == 0:
                messagebox.showinfo("Busca", f"Nenhum dado encontrado para a classe: {classe_sel}")
                
        except Exception as e:
            messagebox.showerror("Erro SPARQL", f"Detalhes do erro:\n{str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = OntologiaDinamica(root)
    root.mainloop()