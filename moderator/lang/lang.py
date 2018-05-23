# encoding: utf-8
from __future__ import unicode_literals


class Commands(object):
    def __init__(self, lang):
        if lang == "cz":
            self.add = "add"
            self.answer = "answer"
            self.ask = "ask"
            self.clear = "clear"
            self.comment = "comment"
            self.delete = "delete"
            self.faq = "faq"
            self.help = "help"
            self.joke = "joke"
            self.list = "list"
            self.media = "media"
            self.rooms = "rooms"

        elif lang == "en":
            self.add = "add"
            self.answer = "answer"
            self.ask = "ask"
            self.clear = "clear"
            self.comment = "comment"
            self.delete = "delete"
            self.faq = "faq"
            self.help = "help"
            self.joke = "joke"
            self.list = "list"
            self.media = "media"
            self.rooms = "rooms"

        else:
            raise LangError("ERROR: Unsupported language - {0}.".format(lang))


class Answers(object):
    def __init__(self, lang):
        self.languages = (
            "cz",
            "en"
        )
        self.mention = "<@personEmail:{0}> "

        if lang == "cz":
            self.yes = "ANO"
            self.no = "NE"
            self.time = "%d.%m. v %H:%M"
            self.unauthorized = "Lituji, ale nejste autorizován k používání tohoto příkazu."
            self.inactive = "Lituji, ale do této místnosti již nemohu nic přidávat."
            self.fallback = "Promiňte, ale nerozumím.\n\nZkuste {0} pro seznam příkazů."
            self.welcome_direct = (
                "Dobrý den **{0}**, já jsem bot moderátor.\n\nNapište **{1}** pro seznam příkazů."
            )
            self.welcome_group = (
                "Dobrý den, já jsem bot moderátor této místnosti.\n\nNapište **{0}** pro seznam příkazů.\n\n"
            )
            self.room_name = "Osobní místnost s {0}"
            self.sql_error = "Ajaj, interní chyba. Administrátor upozorněn. Hned to opravím."

            self.help_all = (
                "Zdravím Vás, **{0}**, rád byste se zeptal či zasmál?\n\n" 
                "Seznam příkazů:\n" 
                "- **{1}  &lt;dotaz&gt;** - pro položení dotazu\n" 
                "- **{2} &lt;číslo dotazu&gt; &lt;komentář&gt;** - pro komentování daného dotazu\n" 
                "- **{3} [číslo dotazu]** - pro seznam dotazů a odpovědí v této místnosti\n" 
                "- **{4}** - pro zobrazení této nápovědy\n" 
                "- **{5}** - pro vtip ze světa IT\n" 
                "- **{6}** - pro zobrazení prezentací a jiných dokumentů\n\n" 
                "Vysvětlivky:\n" 
                "- **&lt;argument&gt;** - povinný argument\n" 
                "- **[argument]** - volitelný argument\n\n" 
                "Příklady příkazů:\n"                
                "- **{1} _Proč jsme tady_?** - položí dotaz a upozorní moderátory diskuze\n"
                "- **{3}** - zobrazí seznam všech FAQ v dané místnosti\n"
                "- **{3} 1** - zobrazí specifické FAQ vlákno včetně odpovědi a komentářů\n"
                "- **{2} 1 _Abychom trpěli._** - okomentuje první FAQ vlákno a upozorní moderátory diskuze\n"
                "- **{6}** - zobrazí seznam všech přednášek a dalších užitečných odkazů\n"
            )
            self.help_admin = (
                "Toto je moderátorská místnost, jste autorizováni k následujícím příkazům:\n" 
                "- **{0} &lt;objekt&gt; [id místnosti] &lt;data&gt;** - pro vložení objektu\n" 
                "- **{1} &lt;id dotazu&gt; &lt;odpověď&gt;** - pro odpověď na dotaz\n" 
                "- **{2} &lt;id místnosti&gt;** - pro smazání všech generovaných zpráv z místnosti\n" 
                "- **{3} &lt;id dotazu&gt; &lt;komentář&gt;** - pro komentování daného dotazu\n" 
                "- **{4} &lt;objekt&gt; &lt;id objektu&gt;** - pro smazání objektu\n" 
                "- **{5} [id dotazu]** - pro zobrazení dané otázky a odpovědí\n" 
                "- **{6}** - pro zobrazení této nápovědy\n" 
                "- **{7}** - pro vtip ze světa IT\n" 
                "- **{8} &lt;objekt&gt; [id místnosti]** - pro zobrazení všech objektů obecně či pro danou místnost\n"
                "- **{9}** - pro zobrazení všech místností\n\n"
                "Typy objektů:\n" 
                "- **{5}** - FAQ\n" 
                "- **{7}** - vtip\n" 
                "- **{10}** - prezentace a jiné dokumenty\n\n" 
                "Vysvětlivky:\n" 
                "- **&lt;argument&gt;** - povinný argument\n" 
                "- **[argument]** - volitelný argument\n\n" 
                "Příklady příkazů:\n" 
                "- **{0} {10} 1 _https://example.com Example presentation_** "
                "- vloží odkaz na prezentaci a odešle notifikaci do místnosti 1\n"
                "- **{0} {5} 2 _Proč jsme tak drazí?_** - manuálně přidá FAQ vlákno do místnosti 2\n"
                "- **{8} {5}** - zobrazí seznam všech FAQ vláken napříč všemi místnostmi\n"
                "- **{1} 4 _Poskytujeme řešení._** - zodpoví otázku FAQ vlákna s číslem 4\n"
                "- **delete faq 1** - odstraní celé FAQ vlákno včetně odpovědi, komentářů a generovaných zpráv\n"
            )
            self.help_group = (
                "**Mějte na paměti, že toto je skupinová místnost. Reaguji pouze, když jsem zmíněn pomocí '@', " 
                "např. <@personEmail:{0}> {1}**\n\nNeváhejte mě však kontaktovat i privátně ve vlastní místnosti."
            )
            self.add_empty = "Nelze vložit prázdný objekt."
            self.add_help = "Zadejte prosím správně argumenty příkazu, nápověda: **{0}{1} &lt;objekt&gt; &lt;data&gt;**"

            self.answer_bad = "Nelze vložit prázdnou odpověď."
            self.answer_empty = "Je mi líto, ale na tento dotaz zatím neznám odpověď.\n\n"
            self.answer_help = (
                "Zadejte prosím správně argumenty příkazu, nápověda: "
                "**{0}{1} &lt;id dotazu&gt; &lt;odpověď&gt;**"
            )
            self.answer_success = "Odpověď úspěšně zaznamenána, upozornění uživateli **{0}** zasláno."
            self.answer_group = (
                "Uživatel {0} odpověděl na dotaz od <@personEmail:{1}>.\n\n"
                "- **Otázka:** \"{2}\"\n- **Odpověď:** \"{3}\""
            )
            self.answer_personal = (
                "Uživatel {0} odpověděl na Váš dotaz.\n\n- **Otázka:** \"{1}\"\n- **Odpověď:** \"{2}\""
            )
            self.answer_text = "Otázka:\n\n{0}\nOdpověď"

            self.ask_empty = "Nelze vložit prázdný dotaz."
            self.ask_help = (
                "Pro vložení dotazu z moderátorské místnosti napište **{0}{1} {2} &lt;id místnosti&gt; Text dotazu**"
            )
            self.ask_success = "Dotaz úspěšně zaznamenán, budete upozorněn při odpovědi na Váš dotaz."
            self.ask_posted = (
                "Uživatel **{0}** právě položil dotaz:\n\n**\"{1}\"**\n\n" 
                "Pro odpověď napište **<@personEmail:{2}> {3} {4} Text odpovědi**"
            )

            self.clear_help = (
                "Pro smazaní všech generovaných zpráv z dané místnosti napište "
                "**{0}{1} &lt;id místnosti&gt;**"
            )
            self.clear_success = "Zprávy úspěšně smazány."

            self.comment_empty = "Nelze vložit prázdný komentář."
            self.comment_header = "Komentáře:\n\n"
            self.comment_help = (
                "Zadejte prosím správně argumenty příkazu, nápověda: "
                "**{0}{1} &lt;číslo dotazu&gt; &lt;comment&gt;**"
            )
            self.comment_success = "Komentář úspěšně zaznamenán, budete upozorněn při dalších komentářích."
            self.comment_group = (
                "Uživatel **{0}** právě okomentoval dotaz od **{1}**.\n\n"
                "- **Otázka:** \"{2}\"\n- **Komentář:** \"{3}\"\n\n" 
                "Pro další komentář napište **{4}{5} {6} Text komentáře**"
            )
            self.comment_personal = (
                "Uživatel **{0}** právě okomentoval Váš dotaz.\n\n- **Otázka:** \"{1}\"\n- **Komentář:** \"{2}\"\n\n" 
                "Pro další komentář napište **{3} {4} Text komentáře**"
            )
            self.comment_moderator = (
                "Uživatel **{0}** právě okomentoval dotaz od **{1}**.\n\n"
                "- **Otázka:** \"{2}\"\n- **Komentář:** \"{3}\"\n\n" 
                "Pro další komentář napište **{4}{5} {6} Text komentáře**"
            )

            self.delete_help = (
                "Zadejte prosím správně argumenty příkazu, nápověda: "
                "**{0}{1} &lt;objekt&gt; &lt;id objektu&gt;**"
            )

            self.faq_bad = "Zadejte prosím platné číslo dotazu, pro seznam všech dotazů napište **{0}{1}**"
            self.faq_deleted = "Vlákno dotazu včetně komentářů úspěšně smazáno."
            self.faq_empty = "Je mi líto, ale nebyly zatím položeny žádné dotazy."
            self.faq_line = "{0} od uživatele **{1}**: \"{2}\" - Zodpovězena: {3}\n"
            self.faq_thread = "Otázka:\n\n{0}\nOdpověď:\n\n{1}\n"

            self.joke_bad = "Zadejte prosím platné ID vtipu, pro seznam všech vtipů napište **{0}{1} {2}**"
            self.joke_deleted = "Vtip úspěšně smazán."
            self.joke_empty = "Je mi líto, ale zatím neznám žádné vtipy."
            self.joke_success = "Vtip úspěšně uložen, snad se každý pobaví."

            self.list_help = (
                "Zadejte prosím správně argumenty příkazu, nápověda: "
                "**{0}{1} &lt;objekt&gt; [id místnosti]**"
            )
            self.list_empty = "Je mi líto, ale nebyly nalezeny žádné objekty."

            self.media_bad = "Zadejte prosím platné ID dokumentu, pro seznam všech dokumentů napište **{0}{1} {2}**"
            self.media_deleted = "Dokument úspěšně smazán."
            self.media_empty = "Je mi líto, ale zatím nebyly publikovány žádné prezentace či jiné dokumenty."
            self.media_posted = "Uživatel **{0}** právě přidal nový dokument - **[{1}]({2})**"
            self.media_success = "Dokument úspěšně zaznamenán, uživatelé budou upozorněni"

            self.room_bad = "Zadejte prosím platné ID místnosti, pro seznam všech místností napište **{0}{1}**"
            self.room_deleted = "Bot úspěšně odebrán z místnosti úspěšně."
            self.room_direct = "Nelze smazat privátní místnost s uživatelem."
            self.room_empty = "Je mi líto, ale v této místnosti nebyly zatím generovány žádné zprávy."

        elif lang == "en":
            self.yes = "YES"
            self.no = "NO"
            self.time = "%m/%d at %H:%M"
            self.unauthorized = "I am sorry, but you are not authorized to use this command."
            self.inactive = "I am sorry, but I cannot interact with this room anymore."
            self.fallback = "I am sorry, I do not understand.\n\nTry {0} for list of commands."
            self.welcome_direct = (
                "Hello <@personEmail:{0}>, I am the room moderator bot.\n\nType **{1}** for list of commands."
            )
            self.welcome_group = "Hello, I am the room moderator bot.\n\nType **{0}** for list of commands.\n\n"
            self.room_name = "Personal room with {0}"
            self.sql_error = "Oops, internal error. Admin notified. I will fix it right away."

            self.help_all = (
                "Welcome, **{0}**, would you like to ask or laugh?\n\n"
                "List of commands:\n" 
                "- **{1}  &lt;question&gt;** - to ask a question\n" 
                "- **{2} &lt;faq number&gt; &lt;comment&gt;** - to comment the given FAQ thread\n" 
                "- **{3} [faq number]** - to list all FAQs or given FAQ thread\n" 
                "- **{4}** - to show this help\n" 
                "- **{5}** - to read an IT joke\n" 
                "- **{6}** - to show shared presentations and other documents\n\n" 
                "Glossary:\n" 
                "- **&lt;argument&gt;** - mandatory argument\n" 
                "- **[argument]** - optional argument\n\n" 
                "Examples:\n" 
                "- **{1} _Why are we here?_** - will ask the question and notify moderators\n"
                "- **{3}** - will list all FAQ in the room\n"
                "- **{3} 1** - will show the specific FAQ thread with answer and comments\n"
                "- **{2} 1 _Just to suffer._** - will comment the first FAQ thread and notify moderators\n"
                "- **{6}** - will list all media in the room\n"
            )
            self.help_admin = (
                "This is the room for moderators, you are authorized to these commands:\n"
                "- **{0} &lt;object&gt; [room id] &lt;data&gt;** - to add an object\n" 
                "- **{1} &lt;faq id&gt; &lt;answer&gt;** - to answer the question\n" 
                "- **{2} &lt;room id&gt;** - to delete all generated messages from the room\n" 
                "- **{3} &lt;faq id&gt; &lt;comment&gt;** - to comment the given FAQ thread\n" 
                "- **{4} &lt;object&gt; &lt;object id&gt;** - to delete the object\n" 
                "- **{5} [faq id]** - to show given FAQ thread\n" 
                "- **{6}** - to show this help\n" 
                "- **{7}** - to read an IT joke\n" 
                "- **{8} &lt;object&gt; [room id]** - to list all objects or specifically in a given room\n"
                "- **{9}** - to list all rooms\n\n"
                "Object types:\n" 
                "- **{5}** - FAQ\n" 
                "- **{7}** - joke\n" 
                "- **{10}** - presentations and other documents\n\n" 
                "Glossary:\n" 
                "- **&lt;argument&gt;** - mandatory argument\n" 
                "- **[argument]** - optional argument\n\n" 
                "Examples:\n"                 
                "- **{0} {10} 1 _https://example.com Example presentation_** "
                "- will add an presentation and sends notification in the first room\n"
                "- **{0} {5} 2 _Why we are expensive?_** - will manually insert FAQ in the room number 2\n"
                "- **{8} {5}** - will list all FAQs in every room\n"
                "- **{1} 4 _We provide solution._** - will answer the question number 4\n"
                "- **delete faq 1** - will delete FAQ thread including answer, comments and related messages\n"
            )
            self.help_group = (
                "**Keep in mind, that this is a group room. I answer only if I am mentioned by '@', "
                "e.g. <@personEmail:{0}> {1}{2}**\n\nYet, do not hesitate to contact me in your private room."
            )
        
            self.add_empty = "Cannot insert empty object."
            self.add_help = (
                "Please enter the right arguments of the command, hint: "
                "**{0}{1} &lt;object&gt; &lt;data&gt;**"
            )

            self.answer_bad = "Cannot insert empty answer."
            self.answer_empty = "I am sorry, but I do not know the answer yet.\n\n"
            self.answer_help = (
                "Please enter the right arguments of the command, hint: "
                "**{0}{1} &lt;faq id&gt; &lt;answer&gt;**"
            )
            self.answer_success = "Answer successfully sent, user **{0}** has been notified."
            self.answer_group = (
                "User {0} answered the question from <@personEmail:{1}>\n\n"
                "- **Question:** \"{2}\"\n- **Answer:** \"{3}\""
            )
            self.answer_personal = "User {0} answered your question.\n\n- **Question:** \"{1}\"\n- **Answer:** \"{2}\""

            self.ask_empty = "Cannot insert empty question."
            self.ask_help = "To post a FAQ from moderator's room type **{0}{1} {2} &lt;room id&gt; FAQ text**"
            self.ask_success = "Question successfully posted, you will be notified when the question is answered."
            self.ask_posted = (
                "User **{0}** has just asked an question:\n\n**\"{1}\"**"
                "For answer type **<@personEmail:{2}> {3} {4} Answer text**"
            )

            self.clear_help = "To delete all generated messages from room type **{0}{1} &lt;room id&gt;**"
            self.clear_success = "Messages successfully deleted."

            self.comment_empty = "Cannot insert empty comment."
            self.comment_header = "\nComments:\n\n"
            self.comment_help = (
                "Please enter the right arguments of the command, hint: "
                "**{0}{1} &lt;faq id&gt; &lt;comment&gt;**"
            )
            self.comment_success = "Comment successfully posted, you will be notified of other comments."
            self.comment_group = (
                "User **{0}** has just comment the question from **{1}**.\n\n"
                "- **Question:** \"{2}\"\n- **Comment:** \"{3}\"\n\n"
                "For next comment type **{4}{5} {6} Comment text**"
            )
            self.comment_personal = (
                "User **{0}** has just commented your question.\n\n"
                "- **Question:** \"{1}\"\n- **Comment:** \"{2}\"\n\n"
                "For next comment type **{3} {4} Comment text**"
            )
            self.comment_moderator = (
                "User **{0}** has just comment the question from **{1}**.\n\n"
                "- **Question:** \"{2}\"\n- **Comment:** \"{3}\"\n\n"
                "For next comment type **{4}{5} {6} Comment text**"
            )

            self.delete_help = (
                "Please enter the right arguments of the command, hint: "
                "**{0}{1} &lt;object&gt; &lt;data&gt;**"
            )

            self.faq_bad = "Please insert a valid FAQ number, to list all FAQs type **{0}{1}**"
            self.faq_deleted = "FAQ thread successfully deleted."
            self.faq_empty = "I am sorry, but no answers have been asked yet."
            self.faq_line = "{0} from user **{1}**: \"{2}\" - Answered: {3}\n"
            self.faq_thread = "Question:\n\n{0}\nAnswer:\n\n{1}\n\n"

            self.joke_bad = "Please enter the valid joke ID, to list all jokes type **{0}{1} {2}**"
            self.joke_deleted = "Joke successfully deleted."
            self.joke_empty = "I am sorry, but I do not know any jokes yet."
            self.joke_success = "Joke successfully inserted, hopefully everybody will laugh."

            self.list_help = (
                "Please enter the right arguments of the command, hint: "
                "**{0}{1} &lt;object&gt; [room id]**"
            )
            self.list_empty = "I am sorry, but no objects have been found."

            self.media_bad = "Please enter the valid document ID, to list all documents type **{0}{1} {2}**"
            self.media_deleted = "Document successfully deleted."
            self.media_empty = "I am sorry, but no presentations or other documents have been published yet."
            self.media_posted = "User **{0}** has just posted new document - **[{1}]({2})**"
            self.media_success = "Document successfully posted, users will be notified."

            self.room_bad = "Please enter the valid room ID, to list all rooms type **{0}{1}**"
            self.room_deleted = "Bot successfully removed from the room."
            self.room_direct = "Cannot delete private room with a user."
            self.room_empty = "I am sorry, but no messages have been generated in this room yet."

        else:
            raise LangError("Unsupported language - {0}.".format(lang))

    def check_lang(self, lang):
        if lang in self.languages:
            return True
        else:
            return False


class LangError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
