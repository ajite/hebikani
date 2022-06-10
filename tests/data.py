"""Test data from WaniKani API."""

API_KEY = "API_KEY"

get_summary = {
    "object": "report",
    "url": "https://api.wanikani.com/v2/summary",
    "data_updated_at": "2018-04-11T00:00:00.000000Z",
    "data": {
        "lessons": [
            {"available_at": "2018-04-11T00:00:00.000000Z", "subject_ids": [25, 26]}
        ],
        "next_reviews_at": "2018-04-11T11:00:00.000000Z",
        "reviews": [
            {
                "available_at": "2018-04-11T00:00:00.000000Z",
                "subject_ids": [21, 23, 24],
            },
            {
                "available_at": "2018-04-11T10:00:00.000000Z",
                "subject_ids": [27, 28, 29],
            },
            {"available_at": "2018-04-11T13:00:00.000000Z", "subject_ids": []},
            {"available_at": "2018-04-11T15:00:00.000000Z", "subject_ids": [30, 31]},
        ],
    },
}

get_specific_subjects = {
    "object": "collection",
    "url": "https://api.wanikani.com/v2/subjects?types=kanji",
    "pages": {
        "per_page": 1000,
        "next_url": "https://api.wanikani.com/v2/subjects?page_after_id=1439\u0026types=kanji",
        "previous_url": None,
    },
    "total_count": 2027,
    "data_updated_at": "2018-04-09T18:08:59.946969Z",
    "data": [
        {
            "id": 440,
            "object": "kanji",
            "url": "https://api.wanikani.com/v2/subjects/440",
            "data_updated_at": "2018-03-29T23:14:30.805034Z",
            "data": {
                "created_at": "2012-02-27T19:55:19.000000Z",
                "level": 1,
                "slug": "一",
                "hidden_at": None,
                "document_url": "https://www.wanikani.com/kanji/%E4%B8%80",
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
    "url": "https://api.wanikani.com/v2/subjects?ids=8769",
    "pages": {"per_page": 1000, "next_url": None, "previous_url": None},
    "total_count": 1,
    "data_updated_at": "2022-05-02T19:28:05.752635Z",
    "data": [
        {
            "id": 8769,
            "object": "radical",
            "url": "https://api.wanikani.com/v2/subjects/8769",
            "data_updated_at": "2021-10-11T22:20:15.393206Z",
            "data": {
                "created_at": "2012-03-03T04:09:15.000000Z",
                "level": 5,
                "slug": "viking",
                "hidden_at": None,
                "document_url": "https://www.wanikani.com/radicals/fake_meaning",
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
    "url": "https://api.wanikani.com/v2/subjects/2467",
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
        "document_url": "https://www.wanikani.com/vocabulary/%E4%B8%80",
        "hidden_at": None,
        "lesson_position": 44,
        "level": 1,
        "meanings": [{"meaning": "One", "primary": True, "accepted_answer": True}],
        "meaning_mnemonic": "As is the case with most vocab words that consist of a single kanji, this vocab word has the same meaning as the kanji it parallels, which is \u003cvocabulary\u003eone\u003c/vocabulary\u003e.",
        "parts_of_speech": ["numeral"],
        "pronunciation_audios": [
            {
                "url": "https://cdn.wanikani.com/audios/3020-subject-2467.mp3?1547862356",
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
                "url": "https://cdn.wanikani.com/audios/3018-subject-2467.ogg?1547862356",
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
                "url": "https://cdn.wanikani.com/audios/3020-subject-2467.mp3?1547862356",
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
    "url": "https://api.wanikani.com/v2/subjects/100",
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
        "document_url": "https://www.wanikani.com/vocabulary/%E4%B8%80",
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
    "url": "https://api.wanikani.com/v2/assignments",
    "pages": {
        "per_page": 500,
        "next_url": "https://api.wanikani.com/v2/assignments?page_after_id=80469434",
        "previous_url": None,
    },
    "total_count": 1600,
    "data_updated_at": "2017-11-29T19:37:03.571377Z",
    "data": [
        {
            "id": 80463006,
            "object": "assignment",
            "url": "https://api.wanikani.com/v2/assignments/80463006",
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

vocab_katakana_equals_hiragna_subject = {
    "id": 8960,
    "object": "vocabulary",
    "url": "https://api.wanikani.com/v2/subjects/8960",
    "data_updated_at": "2022-01-18T08:08:16.473772Z",
    "data": {
        "created_at": "2021-04-27T12:21:07.720651Z",
        "level": 3,
        "slug": "\u30d9\u30c3\u30c9\u306e\u4e0b",
        "hidden_at": None,
        "document_url": "https://www.wanikani.com/vocabulary/%E3%83%99%E3%83%83%E3%83%89%E3%81%AE%E4%B8%8B",
        "characters": "\u30d9\u30c3\u30c9\u306e\u4e0b",
        "meanings": [
            {"meaning": "Under The Bed", "primary": True, "accepted_answer": True},
            {"meaning": "Below The Bed", "primary": False, "accepted_answer": True},
            {"meaning": "Beneath The Bed", "primary": False, "accepted_answer": True},
        ],
        "auxiliary_meanings": [{"type": "whitelist", "meaning": "Underneath The Bed"}],
        "readings": [
            {
                "primary": True,
                "reading": "\u3079\u3063\u3069\u306e\u3057\u305f",
                "accepted_answer": True,
            },
            {
                "primary": False,
                "reading": "\u30d9\u30c3\u30c9\u306e\u3057\u305f",
                "accepted_answer": True,
            },
        ],
        "parts_of_speech": ["expression"],
        "component_subject_ids": [451],
        "meaning_mnemonic": "Lorem Ipsum Dolor",
        "reading_mnemonic": "Lorem Ipsum Dolor",
        "context_sentences": [
            {"en": "Lorem ipsum dolor.", "ja": "\u3079\u3063"},
        ],
        "pronunciation_audios": [
            {
                "url": "https://files.wanikani.com/j6zt8pfxuowvahv3lfc6banwu4m1",
                "metadata·      1234567890-=-04321·90=-09": {
                    "gender": "male",
                    "source_id": 43055,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Kenichi",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/mpeg",
            },
            {
                "url": "https://files.wanikani.com/ez2tq8tht6qwoskqme7y8vz5k0g5",
                "metadata": {
                    "gender": "female",
                    "source_id": 44512,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 1,
                    "voice_actor_name": "Kyoko",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/webm",
            },
            {
                "url": "https://files.wanikani.com/xa3cqlpt9rghk2hnyja4vt2bzuys",
                "metadata": {
                    "gender": "female",
                    "source_id": 44512,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 1,
                    "voice_actor_name": "Kyoko",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/ogg",
            },
            {
                "url": "https://files.wanikani.com/x7u0db82fn8r7v7i6px8u4c8y7f3",
                "metadata": {
                    "gender": "female",
                    "source_id": 44512,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 1,
                    "voice_actor_name": "Kyoko",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/mpeg",
            },
            {
                "url": "https://files.wanikani.com/4rvxy2h2k07hv0ed3tisufs6gr1p",
                "metadata": {
                    "gender": "male",
                    "source_id": 43055,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Kenichi",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/webm",
            },
            {
                "url": "https://files.wanikani.com/o4mlolxlqveeggpbiboilnhxqkx5",
                "metadata": {
                    "gender": "male",
                    "source_id": 43055,
                    "pronunciation": "\u3079\u3063\u3069\u306e\u3057\u305f",
                    "voice_actor_id": 2,
                    "voice_actor_name": "Kenichi",
                    "voice_description": "Tokyo accent",
                },
                "content_type": "audio/ogg",
            },
        ],
        "lesson_position": 55,
        "spaced_repetition_system_id": 1,
    },
}

post_review = {
    "id": 72,
    "object": "review",
    "url": "https://api.wanikani.com/v2/reviews/72",
    "data_updated_at": "2018-05-13T03:34:54.000000Z",
    "data": {
        "created_at": "2018-05-13T03:34:54.000000Z",
        "assignment_id": 1422,
        "spaced_repetition_system_id": 1,
        "subject_id": 997,
        "starting_srs_stage": 1,
        "ending_srs_stage": 1,
        "incorrect_meaning_answers": 1,
        "incorrect_reading_answers": 2,
    },
    "resources_updated": {
        "assignment": {
            "id": 1422,
            "object": "assignment",
            "url": "https://api.wanikani.com/v2/assignments/1422",
            "data_updated_at": "2018-05-14T03:35:34.180006Z",
            "data": {
                "created_at": "2018-01-24T21:32:38.967244Z",
                "subject_id": 997,
                "subject_type": "vocabulary",
                "level": 2,
                "srs_stage": 1,
                "unlocked_at": "2018-01-24T21:32:39.888359Z",
                "started_at": "2018-01-24T21:52:47.926376Z",
                "passed_at": None,
                "burned_at": None,
                "available_at": "2018-05-14T07:00:00.000000Z",
                "resurrected_at": None,
                "passed": False,
                "resurrected": False,
                "hidden": False,
            },
        },
        "review_statistic": {
            "id": 342,
            "object": "review_statistic",
            "url": "https://api.wanikani.com/v2/review_statistics/342",
            "data_updated_at": "2018-05-14T03:35:34.223515Z",
            "data": {
                "created_at": "2018-01-24T21:35:55.127513Z",
                "subject_id": 997,
                "subject_type": "vocabulary",
                "meaning_correct": 1,
                "meaning_incorrect": 1,
                "meaning_max_streak": 1,
                "meaning_current_streak": 1,
                "reading_correct": 1,
                "reading_incorrect": 2,
                "reading_max_streak": 1,
                "reading_current_streak": 1,
                "percentage_correct": 67,
                "hidden": False,
            },
        },
    },
}
