"""
Development Sample Generator for MS MARCO-XI (Hindi / hi)

Generates data/sample/msmarco_xi_hi_sample.jsonl containing ~100 sample records
matching the exact verified schema of AI4Bharat/MSMARCO-XI.
"""

import os
import json

OUTPUT_PATH = os.path.join("data", "sample", "msmarco_xi_hi_sample.jsonl")

# Sample template themes for generating realistic 100 Hindi QA examples
TOPICS = [
    {
        "query_type": "description",
        "hi_query": "गोवा की राजधानी क्या है और यह क्यों प्रसिद्ध है?",
        "eng_query": "What is the capital of Goa and why is it famous?",
        "hi_answer": "पणजी (Panaji) गोवा की राजधानी है। यह अपने मांडवी नदी तट, औपनिवेशिक पुर्तगाली वास्तुकला और जीवंत संस्कृति के लिए प्रसिद्ध है।",
        "eng_answer": "Panaji is the capital of Goa. It is famous for its Mandovi riverfront, colonial Portuguese architecture, and vibrant culture.",
        "passages_en": [
            "Panaji is the capital of the Indian state of Goa and the headquarters of North Goa district. It lies on the banks of the Mandovi River estuary in the Tiswadi taluka.",
            "Goa is a state on the southwestern coast of India within the Konkan region. It is separated from the Deccan highlands by the Western Ghats.",
            "Panaji was conquered by the Portuguese in 1510 and served as the capital of Portuguese India from 1843."
        ],
        "passages_hi": [
            "पणजी भारतीय राज्य गोवा की राजधानी और उत्तरी गोवा जिले का मुख्यालय है। यह तिसवाड़ी तालुका में मांडवी नदी के मुहाने के तट पर स्थित है।",
            "गोवा भारत के दक्षिण-पश्चिम तट पर कोंकण क्षेत्र के भीतर स्थित एक राज्य है। यह पश्चिमी घाट द्वारा दक्कन के पठार से अलग होता है।",
            "पणजी पर 1510 में पुर्तगालियों का अधिकार हुआ था और 1843 से यह पुर्तगाली भारत की राजधानी रहा।"
        ],
        "is_selected": [1, 0, 0]
    },
    {
        "query_type": "numeric",
        "hi_query": "गोवा में कुल कितने जिले हैं?",
        "eng_query": "How many districts are there in Goa?",
        "hi_answer": "गोवा में केवल 2 जिले हैं: उत्तरी गोवा और दक्षिणी गोवा।",
        "eng_answer": "Goa has only 2 districts: North Goa and South Goa.",
        "passages_en": [
            "Goa is divided into two administrative districts: North Goa with headquarters at Panaji, and South Goa with headquarters at Margao.",
            "India is a federal union comprising 28 states and 8 union territories, each with its own local administrative divisions.",
            "North Goa district covers an area of 1736 square kilometers while South Goa district covers 1966 square kilometers."
        ],
        "passages_hi": [
            "गोवा दो प्रशासनिक जिलों में विभाजित है: उत्तरी गोवा जिसका मुख्यालय पणजी में है, और दक्षिणी गोवा जिसका मुख्यालय मडगांव में है।",
            "भारत 28 राज्यों और 8 केंद्र शासित प्रदेशों का एक संघीय संघ है, जिनमें से प्रत्येक का अपना स्थानीय प्रशासनिक विभाजन है।",
            "उत्तरी गोवा जिले का क्षेत्रफल 1736 वर्ग किलोमीटर है जबकि दक्षिणी गोवा जिले का क्षेत्रफल 1966 वर्ग किलोमीटर है।"
        ],
        "is_selected": [1, 0, 0]
    },
    {
        "query_type": "description",
        "hi_query": "रैग (RAG) प्रणाली क्या है और यह कैसे काम करती है?",
        "eng_query": "What is a Retrieval-Augmented Generation (RAG) system and how does it work?",
        "hi_answer": "रैग (Retrieval-Augmented Generation) एक एआई तकनीक है जो भाषा मॉडल को बाहरी ज्ञान आधार से प्रासंगिक जानकारी प्राप्त करके अधिक सटीक और तथ्य-आधारित उत्तर उत्पन्न करने में सक्षम बनाती है।",
        "eng_answer": "Retrieval-Augmented Generation (RAG) is an AI architecture that enhances language models by retrieving relevant information from an external knowledge base to generate accurate, grounded responses.",
        "passages_en": [
            "Retrieval-Augmented Generation (RAG) combines a document retriever with a generative language model to improve response accuracy.",
            "Vector databases store text embeddings and enable efficient semantic search across millions of passage vectors.",
            "Speech recognition systems transcribe spoken voice audio into text format for downstream processing."
        ],
        "passages_hi": [
            "रिट्रीवल-ऑगमेंटेड जनरेशन (RAG) उत्तर की सटीकता में सुधार के लिए एक दस्तावेज़ रिट्रीवर को एक जनरेटिव भाषा मॉडल के साथ जोड़ता है।",
            "वेक्टर डेटाबेस टेक्स्ट एम्बेडिंग को संग्रहीत करते हैं और लाखों पैसेज वेक्टरों में कुशल अर्थ संबंधी खोज सक्षम करते हैं।",
            "स्पीच रिकॉग्निशन सिस्टम बोले गए वॉयस ऑडियो को डाउनस्ट्रीम प्रोसेसिंग के लिए टेक्स्ट फॉर्मेट में ट्रांसक्राइब करते हैं।"
        ],
        "is_selected": [1, 0, 0]
    },
    {
        "query_type": "entity",
        "hi_query": "वाक्यांश से पाठ (Speech-to-Text) ट्रांसक्रिप्शन के लिए कौन सा भारतीय एआई मॉडल प्रयोग किया जाता है?",
        "eng_query": "Which Indian AI model is used for Speech-to-Text transcription?",
        "hi_answer": "सर्वाम (Sarvam AI) का सारस (Saaras) मॉडल भारतीय भाषाओं में उच्च सटीकता के साथ वॉयस ट्रांसक्रिप्शन प्रदान करता है।",
        "eng_answer": "Sarvam AI's Saaras model provides high-accuracy speech-to-text transcription for Indian languages.",
        "passages_en": [
            "Sarvam AI is an Indian artificial intelligence startup building domain-specific LLMs and speech tools tailored for Indic languages.",
            "FAISS is an open-source library created by Facebook AI Research for efficient similarity search and vector index matching.",
            "FastAPI is a modern high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints."
        ],
        "passages_hi": [
            "सर्वाम एआई (Sarvam AI) एक भारतीय आर्टिफिशियल इंटेलिजेंस स्टार्टअप है जो भारतीय भाषाओं के लिए विशेष एलएलएम और स्पीच टूल बनाता है।",
            "FAISS फेसबुक एआई रिसर्च द्वारा निर्मित एक ओपन-सोर्स लाइब्रेरी है जो कुशल समानता खोज और वेक्टर इंडेक्स मिलान के लिए उपयोग की जाती है।",
            "FastAPI मानक पाइथन टाइप संकेत पर आधारित पाइथन 3.8+ के साथ एपीआई बनाने के लिए एक आधुनिक उच्च-प्रदर्शन वेब फ्रेमवर्क है।"
        ],
        "is_selected": [1, 0, 0]
    },
    {
        "query_type": "location",
        "hi_query": "दूधसागर जलप्रपात कहाँ स्थित है?",
        "eng_query": "Where is Dudhsagar Waterfall located?",
        "hi_answer": "दूधसागर जलप्रपात गोवा और कर्नाटक की सीमा पर मांडवी नदी पर स्थित चार स्तरीय जलप्रपात है।",
        "eng_answer": "Dudhsagar Waterfall is a four-tiered waterfall located on the Mandovi River on the border of Goa and Karnataka.",
        "passages_en": [
            "Dudhsagar Falls is a four-tiered waterfall located on the Mandovi River in the Indian state of Goa. It is 60 km from Panaji by road.",
            "The Western Ghats is a mountain range that covers an area of 160,000 square kilometres in a stretch parallel to the western coast of the Indian peninsula.",
            "Bhagwan Mahaveer Sanctuary and Mollem National Park is a 240 square kilometre protected area located in the Western Ghats of South Goa."
        ],
        "passages_hi": [
            "दूधसागर जलप्रपात भारतीय राज्य गोवा में मांडवी नदी पर स्थित एक चार स्तरीय जलप्रपात है। यह सड़क मार्ग से पणजी से 60 किमी दूर है।",
            "पश्चिमी घाट एक पर्वत श्रृंखला है जो भारतीय प्रायद्वीप के पश्चिमी तट के समानांतर 160,000 वर्ग किलोमीटर क्षेत्र को कवर करती है।",
            "भगवान महावीर अभयारण्य और मोल्लेम राष्ट्रीय उद्यान दक्षिण गोवा के पश्चिमी घाट में स्थित 240 वर्ग किलोमीटर का संरक्षित क्षेत्र है।"
        ],
        "is_selected": [1, 0, 0]
    }
]


def generate_sample_records(count: int = 100):
    records = []
    base_id = 100000

    for i in range(count):
        theme = TOPICS[i % len(TOPICS)]
        q_id = base_id + i + 1

        record = {
            "source_lang": "en",
            "target_lang": "hi",
            "query_id": q_id,
            "query_type": theme["query_type"],
            "query": f"{theme['hi_query']} (नमूना {i+1})",
            "Answer": theme["hi_answer"],
            "Eng_Query": f"{theme['eng_query']} (Sample {i+1})",
            "Eng_Answer": theme["eng_answer"],
            "meta": {
                "model_name": "IndicTrans2",
                "temperature": 0.0,
                "max_tokens": 512,
                "top_p": 1.0,
                "frequency_penalty": 0,
                "presence_penalty": 0
            },
            "passages": {
                "English_passages": theme["passages_en"],
                "Translated_passages": theme["passages_hi"],
                "is_selected": theme["is_selected"]
            }
        }
        records.append(record)

    return records


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    records = generate_sample_records(100)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Successfully generated {len(records)} records in '{OUTPUT_PATH}'.")
    print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.2f} KB")


if __name__ == "__main__":
    main()
