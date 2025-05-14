
import chromadb
from chromadb.utils import embedding_functions
import time
import multiprocessing as mp
import csv
import random

def producer(filename, batch_size, queue):

    # Load sample data (a restaurant menu of items)
    with open(filename, encoding='utf8') as file:
        lines = csv.reader(file)
        next(lines) # skip column header

        id = 2 # start id=2 to match the id with the line number in the csv (skipping the row 1 column header)

        # Store the name of the menu items in this array. In Chroma, a "document" is a string i.e. name, sentence, paragraph, etc.
        documents = []

        # Store the corresponding menu item IDs in this array.
        metadatas = []

        # Each "document" needs a unique ID. This is like the primary key of a relational database. We'll start at 1 and increment from there.
        ids = []

        # Loop thru each line and populate the 3 arrays.
        for line in lines:

            # Construct document usings csv values
            document = f"{line[11]}"
            
           

            documents.append(document)
            #metadatas.append({"speaker": line[0], "episode": line[2], "season": line[3]})
            ids.append(str(id))
            
            metadatas.append({"ideater":str(id)})


            if len(ids)>=batch_size:
                queue.put((documents, metadatas, ids))
                documents = []
                metadatas = []
                ids = []

            id+=1

        # Queue last batch
        if(len(ids)>0):
            queue.put((documents, metadatas, ids))

# Worker function to get items from the queue
def consumer(use_cuda, queue):
    # Instantiate chromadb instance. Data is stored on disk (a folder named 'my_vectordb' will be created in the same folder as this file).
    chroma_client = chromadb.PersistentClient(path="my_vectordb")

    device = 'cuda' if use_cuda else 'cpu'

    # Select the embedding model to use.
    # List of model names can be found here https://www.sbert.net/docs/pretrained_models.html
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-mpnet-base-dot-v1", device=use_cuda)

    # Create the collection, aka vector database. Or, if database already exist, then use it. Specify the model that we want to use to do the embedding.
    collection = chroma_client.get_or_create_collection(name="my_vectordb", embedding_function=sentence_transformer_ef)

    
    while True:
        # Check for items in queue, this process blocks until queue has items to process.
        batch = queue.get()
        if batch is None:
            break
        
        # Add to collection
        collection.add(
            documents=batch[0],
            metadatas=batch[1],
            ids=batch[2]
        )

if __name__ == "__main__":

    chroma_client = chromadb.PersistentClient(path="my_vectordb")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

    # For cleaner reloading, delete and recreate collection  
    try:
        chroma_client.get_collection(name="got")
        chroma_client.delete_collection(name="got")
    except Exception as err:
        print(err)

    collection = chroma_client.get_or_create_collection(name="got", embedding_function=sentence_transformer_ef)

    # Create a shared queue
    queue = mp.Queue()

    # Create producer and consumer processes.
    producer_process = mp.Process(target=producer, args=('combined_jobs.csv', 500, queue,))
    consumer_process = mp.Process(target=consumer, args=(True, queue,))
    # Do not create multiple consumer processes, because ChromaDB is not multiprocess safe.

    start_time = time.time()

    # Start processes
    producer_process.start()
    consumer_process.start()

    # Wait for producer to finish producing
    producer_process.join()

    # Signal consumer to stop consuming by putting None into the queue. Need 2 None's to stop 2 consumers.    
    queue.put(None)

    # Wait for consumer to finish consuming
    consumer_process.join()

    print(f"Elapsed seconds: {time.time()-start_time:.0f} Record count: {collection.count()}")


    # Query the vector database

# Query mispelled word: 'vermiceli'. Expect to find the correctly spelled 'vermicelli' item
results = collection.query(
    query_texts=["Artificial intelligence"],
    n_results=5,
    include=['documents', 'distances']
)
print(results['documents'])

# Query word variation: 'donut'. Expect to find the 'doughnut' item
results = collection.query(
    query_texts=["Network engineer"],
    n_results=5,
    include=['documents', 'distances']
)
print(results['documents'])

# Query similar meaning: 'shrimp'. Expect to find the 'prawn' items
results = collection.query(
    query_texts=["give only the names of database engineer who works with AI"],
    n_results=5,
    include=['documents', 'distances']
)
print(results['documents'])

    