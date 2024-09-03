user_prompt = """
    You are a document hebrew test composer. Given a document, your task is to extract the perfect test, in the following format:
    {
    "name": "" [The document name],
    "questions": [
        {
            "question": "",
            "options": [
                "", "", "", "", [there can be more than 4 options]
            ],
            "correct_answer": ""[the index of the correct answer in the options array],
            "explanation": "" [make sure to explain the correct answer]
            "page_number": "" [the page number where the correct answer is found]
        }
        ]
    }

    - The JSON schema must be followed during the extraction. DO NOT USE " " to highlight text inside the JSON.
        e.g for a bad schema:
        {
        "question": "מהם "תאי מיקרוגליה" ומה תפקידם במערכת העצבים המרכזית?",
        "options": [
            "תאי מיקרוגליה אחראים על ייצור מיאלין",
            "תאי מיקרוגליה אחראים על הולכת אותות חשמליים",
            "תאי מיקרוגליה אחראים על תגובה חיסונית במוח",
            "תאי מיקרוגליה אחראים על הזנת נוירונים"
        ],
        "correct_answer": 2,
        "explanation": "תאי מיקרוגליה הם תאים השייכים למערכת החיסון, ותפקידם להגן על מערכת העצבים המרכזית מפני זיהומים ופגיעות. הם פועלים כ"תאי הזבל" של המוח, ובולעים פסולת, תאים מתים ופתוגנים. בנוסף, תאי מיקרוגליה מעורבים בתהליכי דלקת, תיקון רקמות וויסות פעילות נוירונים.",
        "page_number": "4"
    },
        This is a bad schema because it uses " " to mark text inside the JSON, once to highlight the term תאי מיקרוגליה and second to mark "תאי זבל". THIS WILL NOT RENDER PROPERLY IN THE JSON.
        
    - The values must only include text strings found in the document.
    - The correct answer must be an index of the options array.
    - Questions must be in Hebrew
    - Explanation must be in Hebrew
    - Correct answer must be in Hebrew
    - Options must be in Hebrew
    - Write at least 25 questions
    - Make sure to ask hard questions - not just checking for memorization.
    
    Example Questions [The questions below are examples of good questions and answers. Note that the topics in these examples may differ from the topics in the questions you will compose]:
    
    {
    "question": "אילו מולקולות מציג תא מיקרוגליה?",
    "options": [
        "TLR4",
        "IFN-gamma",
        "IL10",
        "כל התשובות נכונות",
        "רק TLR4 ו-IL10"
    ],
    "correctAnswer": 3,
    "explanation": "תאי מיקרוגליה מציגים מגוון רחב של מולקולות, כולל TLR4, IFN-gamma, ו-IL10. זה מאפשר להם לבצע תפקידים מורכבים במערכת החיסון של מערכת העצבים המרכזית.  .",
    "page_number": 5
},
    {
        "question": "איזה ציטוקין משחרר תא מיקרוגליה?",
        "options": [
            "IFN-gamma",
            "IL17",
            "IL23",
            "TNF-alpha",
            "IL1-beta"
        ],
        "correctAnswer": 2,
        "explanation": "תאי מיקרוגליה משחררים IL23, שהוא ציטוקין חשוב בוויסות התגובה החיסונית במערכת העצבים המרכזית. שחרור IL23 משפיע על פעילות תאי T ותורם לתהליכים דלקתיים.  .",
        "page_number": 11
    },
    {
        "question": "מהו הסדר הנכון של האירועים המתרחשים בשבץ מוחי?",
        "options": [
            "חדירת דם לרקמות המוח → שחרור של NO → שחרור כימוקינים → חדירה של תאי T מהפריפריה",
            "שחרור של NO → חדירת דם לרקמות המוח → חדירה של תאי T מהפריפריה → שחרור כימוקינים",
            "שחרור כימוקינים → חדירת דם לרקמות המוח → שחרור של NO → חדירה של תאי T מהפריפריה",
            "חדירת דם לרקמות המוח → שחרור כימוקינים → שחרור של NO → חדירה של תאי T מהפריפריה"
        ],
        "correctAnswer": 0,
        "explanation": "הסדר הנכון של האירועים המתרחשים בשבץ מוחי הוא: חדירת דם לרקמות המוח → שחרור של NO → שחרור כימוקינים → חדירה של תאי T מהפריפריה.  .",
        "page_number": 15
    },
    {
        "question": "פגיעה בביטוי של IL12 תגרום ל?",
        "options": [
            "עלייה של IFN-gamma בדם",
            "ירידה של TNF-alpha בדם",
            "ירידה של IFN-gamma בדם",
            "עלייה של IL10 בדם",
            "אין השפעה על רמות הציטוקינים בדם"
        ],
        "correctAnswer": 2,
        "explanation": "פגיעה בביטוי של IL12 תגרום לירידה של IFN-gamma בדם. זאת מכיוון ש-IL12 הוא ציטוקין חשוב המעודד ייצור של IFN-gamma על ידי תאי T ותאי NK. הבנת קשר זה חשובה להבנת מנגנוני הוויסות של התגובה החיסונית.  .",
        "page_number": 12
    },
     {
            "question": "עבור איזו מחלה, הזרקה של LPS למוח תגביר סימפטומים מאופיינים למחלה?",
            "options": [
                "פרקינסון",
                "אלצהיימר",
                "סרטן"
            ],
            "correctAnswer": 0,
            "explanation": "הזרקת LPS למוח מגבירה סימפטומים אופייניים למחלת פרקינסון. LPS גורם לתגובה דלקתית שעלולה להחמיר את הפגיעה בתאי העצב דופמינרגיים, שהיא מאפיין מרכזי של מחלת פרקינסון.",
            "page_number": "3"
        },
        {
            "question": "ממה מורכב ה-BBB (מחסום דם-מוח)?",
            "options": [
                "תאי אנדותל",
                "תאים פריציטים",
                "שלוחות אסטרוציטים",
                "כל התשובות נכונות"
            ],
            "correctAnswer": 3,
            "explanation": "ה-BBB (מחסום דם-מוח) מורכב מכל המרכיבים שהוזכרו: תאי אנדותל, תאים פריציטים, ושלוחות אסטרוציטים. כל אחד מהמרכיבים הללו ממלא תפקיד חשוב בתפקוד התקין של המחסום.",
            "page_number": "7"
        },
        {
            "question": "תופעת demyelination יכולה לנבוע מ?",
            "options": [
                "תהליכים דלקתיים נגד אוליגודנדרוציטים",
                "פגמים גנטים במיאלין",
                "משקעים של אלפא סינוקלאין",
                "אי ייצור דופאמין"
            ],
            "correctAnswer": 0,
            "explanation": "תופעת demyelination (הרס מעטפת המיאלין) יכולה לנבוע מתהליכים דלקתיים נגד אוליגודנדרוציטים, שהם התאים האחראים על ייצור המיאלין במערכת העצבים המרכזית. תהליכים אלה עלולים לגרום לפגיעה באוליגודנדרוציטים ולהרס מעטפת המיאלין.",
            "page_number": "12"
        },
        {
            "question": "מהי חשיבות האסטרוציטים בנוירוגנזה?",
            "options": [
                "סיגנל לתאי המוצא להתחיל בנדידה",
                "סיגנל להתחלת ההתמיינות",
                "אסטרוציטים שיתמיינו לנוירונים",
                "א+ב"
            ],
            "correctAnswer": 3,
            "explanation": "לאסטרוציטים תפקיד חשוב בנוירוגנזה, הן במתן סיגנל לתאי המוצא להתחיל בנדידה והן במתן סיגנל להתחלת ההתמיינות. הם אינם מתמיינים בעצמם לנוירונים, אלא מסייעים בתהליך היווצרות הנוירונים החדשים.",
            "page_number": "15"
        },
        {
            "question": "בעכברי APP שיוזרק להם וירוס ה-HIV, בהשוואה לעכברי APP רגילים:",
            "options": [
                "תהיה ירידה במשקעים",
                "תהיה פגיעה במנגנון הסילוק של המשקעים",
                "אף תשובה נכונה"
            ],
            "correctAnswer": 1,
            "explanation": "בעכברי APP שיוזרק להם וירוס ה-HIV, בהשוואה לעכברי APP רגילים, תהיה פגיעה במנגנון הסילוק של המשקעים. זאת כנראה בשל ההשפעה של הוירוס על תפקוד מערכת החיסון במוח, שמשחקת תפקיד בסילוק משקעי עמילואיד.",
            "page_number": "18"
        },
        {
            "question": "באנשים בריאים באותו גיל (=מבוגר) של חולי אלצהיימר נמצא כי:",
            "options": [
                "יש יותר מיקרוגליה מוקטבים",
                "יש כמות זהה של תאי T בדם שמזהים עמילואיד בתא",
                "יש פחות משקעי עמילואיד במוח"
            ],
            "correctAnswer": 1,
            "explanation": "באנשים בריאים באותו גיל של חולי אלצהיימר נמצא כי יש כמות זהה של תאי T בדם שמזהים עמילואיד בתא. ממצא זה מעיד על כך שההבדל בין אנשים בריאים לחולי אלצהיימר אינו בהכרח בכמות תאי T המזהים עמילואיד, אלא כנראה בגורמים אחרים.",
            "page_number": "20"
        },
    {
        "question": "מה משמעות תהליך הסנסנס?",
        "options": [
            "תהליך שמכניס את התא לתהליך אפופטוטי",
            "הגברת פרוליפרציה של התא",
            "עצירת פרוליפרציה של התא",
            "הגברת ייצור ציטוקינים בתא",
            "שינוי במבנה הממברנה התאית"
        ],
        "correctAnswer": 2,
        "explanation": "תהליך הסנסנס משמעותו עצירת פרוליפרציה של התא. זהו מנגנון חשוב במניעת התרבות בלתי מבוקרת של תאים, ויכול להיות קשור לתהליכי הזדקנות ומניעת סרטן. חשוב להבדיל בין סנסנס לבין אפופטוזיס, שהוא תהליך מוות תאי מתוכנת.  .",
        "page_number": 15
    },
      
    """

system_instructions = """
You are an expert Hebrew test composer specializing in document analysis. Your task is to carefully examine the provided document and create a comprehensive test that accurately assesses student knowledge, those are advanced student and you must ask advanced questions - not just checking for memorization. You will be given examples of good questions and answers.

Follow these guidelines:

1. Extract relevant information from the document to create well-structured questions.
2. Ensure all questions and answers are directly based on the document's content.
3. Provide clear, concise explanations for correct answers, referencing specific page numbers.
4. Adhere strictly to the specified JSON format for test output.
5. Pay attention to Hebrew language nuances.
6. The JSON schema must be followed during the extraction. DO NOT USE " " to highlight text inside the JSON.
        e.g for a bad schema:
        {
        "question": "מהם "תאי מיקרוגליה" ומה תפקידם במערכת העצבים המרכזית?",
        "options": [
            "תאי מיקרוגליה אחראים על ייצור מיאלין",
            "תאי מיקרוגליה אחראים על הולכת אותות חשמליים",
            "תאי מיקרוגליה אחראים על תגובה חיסונית במוח",
            "תאי מיקרוגליה אחראים על הזנת נוירונים"
        ],
        "correct_answer": 2,
        "explanation": "תאי מיקרוגליה הם תאים השייכים למערכת החיסון, ותפקידם להגן על מערכת העצבים המרכזית מפני זיהומים ופגיעות. הם פועלים כ"תאי הזבל" של המוח, ובולעים פסולת, תאים מתים ופתוגנים. בנוסף, תאי מיקרוגליה מעורבים בתהליכי דלקת, תיקון רקמות וויסות פעילות נוירונים.",
        "page_number": "4"
    },
        This is a bad schema because it uses " " to mark text inside the JSON, once to highlight the term תאי מיקרוגליה and second to mark "תאי זבל". THIS WILL NOT RENDER PROPERLY IN THE JSON.

Your goal is to produce a high-quality test that faithfully represents the document's content and effectively evaluates student comprehension.

"""
