import os
import logging
import json
from flask_cors import CORS
from flask import Flask, request, jsonify
import time

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import DensePassageRetriever, PDFToTextConverter, PreProcessor, ElasticsearchRetriever
from haystack.pipelines import DocumentSearchPipeline

# Application Settings
app = Flask(__name__)
CORS(app)

# Application directory for inputs
app.config['input'] = 'data/input'

# ElasticSearch server host information
app.config['host'] = 'elasticsearch'
app.config['username'] = ''
app.config['password'] = ''
app.config['port'] = '9200'


@app.route('/')
def home():
    """Return a Greeting"""
    return "Welcome to Intelligent Search Engine"


# Endpoint to update Embedded Method
@app.route('/set_embed', methods=['POST'])
def set_embed():
    """Update Embeddings"""
    time.sleep(45)
    print(app.config['host'])
    print(app.config['port'])
    index = request.form['index']
    document_store = ElasticsearchDocumentStore(host=app.config['host'],
                                                port=app.config['port'],
                                                username=app.config['username'],
                                                password=app.config['password'],
                                                index=index,
                                                embedding_field='embedding',
                                                similarity='cosine')
    retriever_pdf = DensePassageRetriever(document_store=document_store,
                                          query_embedding_model='facebook/dpr-question_encoder-single-nq-base',
                                          passage_embedding_model='facebook/dpr-ctx_encoder-single-nq-base')
    document_store.update_embeddings(retriever_pdf)
    return jsonify({'status': 'Success',
                    'message': 'Successfully embed method updated in ElasticSearch Document'})


@app.route('/update_document', methods=['POST'])
def update_document():
    """Return url of the updated document"""
    if request.files:

        # Index is the target document where queries need to send.
        index = request.form['index']
        # Uploaded Document for Target source
        doc = request.files['doc']
        file_path = os.path.join(app.config['input'], doc.filename)
        # Saving the file to the input directory
        doc.save(file_path)
        # Initialization of the Haystack ElasticSearch document storage
        document_store = ElasticsearchDocumentStore(host=app.config['host'],
                                                    port=app.config['port'],
                                                    username=app.config['username'],
                                                    password=app.config['password'],
                                                    index=index)
        # Convert the pdf files into dictionary and update to ElasticSearch Document store
        pdf_converter = PDFToTextConverter(remove_numeric_tables=True,
                                           valid_languages=['en'])
        doc_pdf = pdf_converter.convert(file_path=file_path,
                                        meta=None)[0]
        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=True,
            split_by="word",
            split_length=100,
            split_respect_sentence_boundary=True
        )
        preprocessed_doc_pdf = preprocessor.process([doc_pdf])
        document_store.write_documents(preprocessed_doc_pdf)
        os.remove(file_path)
        return jsonify(
            {'status': 'Success',
             'message': 'document available at http://' + app.config['host'] + ':' + app.config[
                 'port'] + '/' + index + '/_search'})
    else:
        return jsonify({'status': 'Failed',
                        'message': 'No file uploaded'})


@app.route('/semanticsearch', methods=['POST'])
def semanticsearch():
    """Return n answers"""
    query = request.form['query']
    index = request.form['index']
    document_store = ElasticsearchDocumentStore(
        host=app.config['host'],
        username=app.config['username'],
        password=app.config['password'],
        index=index
    )
    retriever = ElasticsearchRetriever(document_store=document_store)
    pipe_df = DocumentSearchPipeline(retriever)
    n = int(request.form['n'])
    prediction = pipe_df.run(
        query=query,
        params={'Retriever': {'top_k': n}}
    )
    answer = [(x.to_dict()['content'], x.to_dict()['score']) for x in prediction['documents']]
    return jsonify({'status': 'Success',
                    'message': 'Search Result is as below:',
                    'result': answer})


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=8777)
