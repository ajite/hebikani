"""Test data from hebikani API."""

API_KEY = "API_KEY"

get_summary = {
    "object": "report",
    "url": "https://api.hebikani.com/v2/summary",
    "data_updated_at": "2018-04-11T21:00:00.000000Z",
    "data": {
        "lessons": [
            {"available_at": "2018-04-11T21:00:00.000000Z", "subject_ids": [25, 26]}
        ],
        "next_reviews_at": "2018-04-11T21:00:00.000000Z",
        "reviews": [
            {
                "available_at": "2018-04-11T21:00:00.000000Z",
                "subject_ids": [21, 23, 24],
            },
            {"available_at": "2018-04-11T22:00:00.000000Z", "subject_ids": []},
        ],
    },
}

get_specific_subjects = {
    "object": "collection",
    "url": "https://api.hebikani.com/v2/subjects?types=kanji",
    "pages": {
        "per_page": 1000,
        "next_url": "https://api.hebikani.com/v2/subjects?page_after_id=1439\u0026types=kanji",
        "previous_url": None,
    },
    "total_count": 2027,
    "data_updated_at": "2018-04-09T18:08:59.946969Z",
    "data": [
        {
            "id": 440,
            "object": "kanji",
            "url": "https://api.hebikani.com/v2/subjects/440",
            "data_updated_at": "2018-03-29T23:14:30.805034Z",
            "data": {
                "created_at": "2012-02-27T19:55:19.000000Z",
                "level": 1,
                "slug": "一",
                "hidden_at": None,
                "document_url": "https://www.hebikani.com/kanji/%E4%B8%80",
                "characters": "一",
                "meanings": [
                    {"meaning": "One", "primary": True, "accepted_answer": True}
                ],
                "readings": [
                    {
                        "type": "onyomi",
                        "primary": True,
                        "accepted_answer": True,
                        "reading": "いち",
                    },
                    {
                        "type": "kunyomi",
                        "primary": False,
                        "accepted_answer": False,
                        "reading": "ひと",
                    },
                    {
                        "type": "nanori",
                        "primary": False,
                        "accepted_answer": False,
                        "reading": "かず",
                    },
                ],
                "component_subject_ids": [1],
                "amalgamation_subject_ids": [56, 88, 91],
                "visually_similar_subject_ids": [],
                "meaning_mnemonic": "Lying on the <radical>ground</radical> is something that looks just like the ground, the number <kanji>One</kanji>. Why is this One lying down? It's been shot by the number two. It's lying there, bleeding out and dying. The number One doesn't have long to live.",
                "meaning_hint": "To remember the meaning of <kanji>One</kanji>, imagine yourself there at the scene of the crime. You grab <kanji>One</kanji> in your arms, trying to prop it up, trying to hear its last words. Instead, it just splatters some blood on your face. \"Who did this to you?\" you ask. The number One points weakly, and you see number Two running off into an alleyway. He's always been jealous of number One and knows he can be number one now that he's taken the real number one out.",
                "reading_mnemonic": "As you're sitting there next to <kanji>One</kanji>, holding him up, you start feeling a weird sensation all over your skin. From the wound comes a fine powder (obviously coming from the special bullet used to kill One) that causes the person it touches to get extremely <reading>itchy</reading> (いち)",
                "reading_hint": "Make sure you feel the ridiculously <reading>itchy</reading> sensation covering your body. It climbs from your hands, where you're holding the number <kanji>One</kanji> up, and then goes through your arms, crawls up your neck, goes down your body, and then covers everything. It becomes uncontrollable, and you're scratching everywhere, writhing on the ground. It's so itchy that it's the most painful thing you've ever experienced (you should imagine this vividly, so you remember the reading of this kanji).",
                "lesson_position": 2,
                "spaced_repetition_system_id": 1,
            },
        }
    ],
}

get_subject_without_utf_entry = {
    "object": "collection",
    "url": "https://api.hebikani.com/v2/subjects?ids=8769",
    "pages": {"per_page": 1000, "next_url": None, "previous_url": None},
    "total_count": 1,
    "data_updated_at": "2022-05-02T19:28:05.752635Z",
    "data": [
        {
            "id": 8769,
            "object": "radical",
            "url": "https://api.hebikani.com/v2/subjects/8769",
            "data_updated_at": "2021-10-11T22:20:15.393206Z",
            "data": {
                "created_at": "2012-03-03T04:09:15.000000Z",
                "level": 5,
                "slug": "viking",
                "hidden_at": None,
                "document_url": "https://www.hebikani.com/radicals/fake_meaning",
                "characters": None,
                "character_images": [
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "1024x1024",
                            "style_name": "original",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "1024x1024",
                            "style_name": "1024px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "512x512",
                            "style_name": "512px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "256x256",
                            "style_name": "256px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "128x128",
                            "style_name": "128px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "64x64",
                            "style_name": "64px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {
                            "color": "#000000",
                            "dimensions": "32x32",
                            "style_name": "32px",
                        },
                        "content_type": "image/png",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {"inline_styles": False},
                        "content_type": "image/svg+xml",
                    },
                    {
                        "url": "fake_path",
                        "metadata": {"inline_styles": True},
                        "content_type": "image/svg+xml",
                    },
                ],
                "meanings": [
                    {
                        "meaning": "Fake meaning",
                        "primary": True,
                        "accepted_answer": True,
                    }
                ],
                "auxiliary_meanings": [],
                "amalgamation_subject_ids": [
                    29492329,
                ],
                "meaning_mnemonic": "Lorem Ipsum Dolor Sit Amet",
                "lesson_position": 3909,
                "spaced_repetition_system_id": 1,
            },
        }
    ],
}

vocabulary_subject = {
    "id": 2467,
    "object": "vocabulary",
    "url": "https://api.hebikani.com/v2/subjects/2467",
    "data_updated_at": "2018-12-12T23:09:52.234049Z",
    "data": {
        "auxiliary_meanings": [{"type": "whitelist", "meaning": "1"}],
        "characters": "一",
        "component_subject_ids": [440],
        "context_sentences": [
            {"en": "Let’s meet up once.", "ja": "一ど、あいましょう。"},
            {"en": "First place was an American.", "ja": "一いはアメリカ人でした。"},
            {"en": "I’m the weakest man in the world.", "ja": "ぼくはせかいで一ばんよわい。"},
        ],
        "created_at": "2012-02-28T08:04:47.000000Z",
        "document_url": "https://www.hebikani.com/vocabulary/%E4%B8%80",
        "hidden_at": None,
        "lesson_position": 44,
        "level": 1,
        "meanings": [{"meaning": "One", "primary": True, "accepted_answer": True}],
        "meaning_mnemonic": "As is the case with most vocab words that consist of a single kanji, this vocab word has the same meaning as the kanji it parallels, which is \u003cvocabulary\u003eone\u003c/vocabulary\u003e.",
        "parts_of_speech": ["numeral"],
        "pronunciation_audios": [
            {
                "url": "https://cdn.hebikani.com/audios/3020-subject-2467.mp3?1547862356",
                "metadata": {
                    "gender": "male",
                    "source_id": 2711,
                    "pronunciation": "いち",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Kenichi",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/mpeg",
            },
            {
                "url": "https://cdn.hebikani.com/audios/3018-subject-2467.ogg?1547862356",
                "metadata": {
                    "gender": "male",
                    "source_id": 2711,
                    "pronunciation": "いち",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Kenichi",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/ogg",
            },
            {
                "url": "https://cdn.hebikani.com/audios/3020-subject-2467.mp3?1547862356",
                "metadata": {
                    "gender": "female",
                    "source_id": 2711,
                    "pronunciation": "いち",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Yoko",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/mpeg",
            },
        ],
        "readings": [{"primary": True, "reading": "いち", "accepted_answer": True}],
        "reading_mnemonic": "When a vocab word is all alone and has no okurigana (hiragana attached to kanji) connected to it, it usually uses the kun'yomi reading. Numbers are an exception, however. When a number is all alone, with no kanji or okurigana, it is going to be the on'yomi reading, which you learned with the kanji.  Just remember this exception for alone numbers and you'll be able to read future number-related vocab to come.",
        "slug": "一",
        "spaced_repetition_system_id": 1,
    },
}

double_reading_subject = {
    "id": 100,
    "object": "kanji",
    "url": "https://api.hebikani.com/v2/subjects/100",
    "data_updated_at": "2018-12-12T23:09:52.234049Z",
    "data": {
        "auxiliary_meanings": [{"type": "whitelist", "meaning": "1"}],
        "characters": "何",
        "component_subject_ids": [440],
        "context_sentences": [
            {"en": "Let’s meet up once.", "ja": "一ど、あいましょう。"},
            {"en": "First place was an American.", "ja": "一いはアメリカ人でした。"},
            {"en": "I’m the weakest man in the world.", "ja": "ぼくはせかいで一ばんよわい。"},
        ],
        "created_at": "2012-02-28T08:04:47.000000Z",
        "document_url": "https://www.hebikani.com/vocabulary/%E4%B8%80",
        "hidden_at": None,
        "lesson_position": 44,
        "level": 1,
        "meanings": [{"meaning": "What", "primary": True, "accepted_answer": True}],
        "meaning_mnemonic": "As is the case with most vocab words that consist of a single kanji, this vocab word has the same meaning as the kanji it parallels, which is \u003cvocabulary\u003eone\u003c/vocabulary\u003e.",
        "parts_of_speech": ["numeral"],
        "readings": [
            {"primary": True, "reading": "なに", "accepted_answer": True},
            {"primary": False, "reading": "なん", "accepted_answer": True},
            {
                "type": "kunyomi",
                "primary": False,
                "accepted_answer": False,
                "reading": "はははは",
            },
        ],
        "reading_mnemonic": "When a vocab word is all alone and has no okurigana (hiragana attached to kanji) connected to it, it usually uses the kun'yomi reading. Numbers are an exception, however. When a number is all alone, with no kanji or okurigana, it is going to be the on'yomi reading, which you learned with the kanji.  Just remember this exception for alone numbers and you'll be able to read future number-related vocab to come.",
        "slug": "一",
        "spaced_repetition_system_id": 1,
    },
}


get_all_assignments = {
    "object": "collection",
    "url": "https://api.hebikani.com/v2/assignments",
    "pages": {
        "per_page": 500,
        "next_url": "https://api.hebikani.com/v2/assignments?page_after_id=80469434",
        "previous_url": None,
    },
    "total_count": 1600,
    "data_updated_at": "2017-11-29T19:37:03.571377Z",
    "data": [
        {
            "id": 80463006,
            "object": "assignment",
            "url": "https://api.hebikani.com/v2/assignments/80463006",
            "data_updated_at": "2017-10-30T01:51:10.438432Z",
            "data": {
                "created_at": "2017-09-05T23:38:10.695133Z",
                "subject_id": 8761,
                "subject_type": "radical",
                "srs_stage": 8,
                "unlocked_at": "2017-09-05T23:38:10.695133Z",
                "started_at": "2017-09-05T23:41:28.980679Z",
                "passed_at": "2017-09-07T17:14:14.491889Z",
                "burned_at": None,
                "available_at": "2018-02-27T00:00:00.000000Z",
                "resurrected_at": None,
            },
        }
    ],
}
