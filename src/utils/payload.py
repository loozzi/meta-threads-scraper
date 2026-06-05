import json


RELAY_FLAGS_MINIMAL = {
    '__relay_internal__pv__BarcelonaIsInternalUserrelayprovider': False,
    '__relay_internal__pv__BarcelonaIsLoggedInrelayprovider': False,
    '__relay_internal__pv__BarcelonaIsCrawlerrelayprovider': False,
}

_RELAY_FLAGS_BASE = {
    '__relay_internal__pv__BarcelonaIsLoggedInrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasDearAlgoConsumptionrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasEventBadgerelayprovider': False,
    '__relay_internal__pv__BarcelonaGenAIRepliesEnabledrelayprovider': False,
    '__relay_internal__pv__BarcelonaIsSearchDiscoveryEnabledrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasCommunitiesrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasGameScoreSharerelayprovider': True,
    '__relay_internal__pv__BarcelonaHasPublicViewCountCardrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasCommunityEntityCardrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasScorecardCommunityrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasMusicrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasNewspaperLinkStylerelayprovider': False,
    '__relay_internal__pv__BarcelonaHasMessagingrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasViewerRepliedrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasGhostPostEmojiActivationrelayprovider': False,
    '__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasDearAlgoWebProductionrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasWebFaviconsrelayprovider': False,
    '__relay_internal__pv__BarcelonaIsCrawlerrelayprovider': False,
    '__relay_internal__pv__BarcelonaHasCommunityTopContributorsrelayprovider': False,
    '__relay_internal__pv__BarcelonaCanSeeSponsoredContentrelayprovider': False,
    '__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider': False,
    '__relay_internal__pv__BarcelonaIsInternalUserrelayprovider': False,
}

# Logged-in bật thêm mấy flag này
_RELAY_LOGGED_IN_OVERRIDES = {
    '__relay_internal__pv__BarcelonaIsLoggedInrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasCommunityEntityCardrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasScorecardCommunityrelayprovider': True,
    '__relay_internal__pv__BarcelonaHasMessagingrelayprovider': True,
    '__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider': True,
}

def _get_payload(
        doc_id: str,
        friendly_name: str,
        variables: str,
        # --- auth context ---
        av: str = "0",
        # --- optional extras ---
        crn: str = None,
    ) -> dict:
        """
        Build a Threads GraphQL payload.
        """
        payload = {
            "av": av,
            "fb_api_req_friendly_name": friendly_name,
            "variables": variables,
            "doc_id": doc_id,
            "__user": "0",
            "fb_api_caller_class": "RelayModern",
            "server_timestamps": "true",
            "__a": "1",
            "dpr": "1",
        }

        if crn:
            payload["__crn"] = crn

        return payload

def get_relay_flags(logged_in: bool = False) -> dict:
    flags = {**_RELAY_FLAGS_BASE}
    if logged_in:
        flags.update(_RELAY_LOGGED_IN_OVERRIDES)
    return flags


def get_search_payload(query: str, limit: int = 10) -> dict:
    variables = {
        'query': query,
        'first': limit,
        'should_fetch_ig_inactive_on_text_app': None,
        'should_fetch_friendship_status': False,
        'should_fetch_fediverse_profiles': False,
        'hide_unconnected_private': False,
        'is_internal_user': False,
        **RELAY_FLAGS_MINIMAL,
    }
    return _get_payload(
        doc_id="27483363884603624",
        friendly_name="useBarcelonaAccountSearchGraphQLDataSourceQuery",
        variables=json.dumps(variables)
    )

def get_feed_payload(limit: int = 10, cursor_after: str = None, logged_in: bool = False) -> dict:
    if logged_in:
        variables = {
            'after': cursor_after,
            'before': None,
            'first': limit,
            'last': None,
            'sort_by': None,
            'variant': 'for_you',
            'data': {
                'feed_view_info': '[]',
                'pagination_source': 'text_post_feed_threads',
                'reason': 'pagination',
            },
            **get_relay_flags(logged_in=True),
        }
        return _get_payload(
            doc_id="36272699522373817",
            friendly_name="BarcelonaFeedPaginationDirectQuery",
            crn="comet.threads.BarcelonaHomeRouteV2",
            variables=json.dumps(variables)
        )
    else:
        variables = {
            'after': cursor_after,
            'before': None,
            'first': 10,
            'injected_media_ids': None,
            'last': None,
            'specified_country': "ROW",
            **get_relay_flags(logged_in=False),
        }
        return _get_payload(
            doc_id="28224140877186477",
            friendly_name="BarcelonaLoggedOutFeedPaginationQuery",
            variables=json.dumps(variables)
        )


def get_user_payload(user_id: str, cursor_after: str = None) -> dict:
    variables = {
        'after': cursor_after,
        'allow_page_info_for_lox_user': True,
        'before': None,
        'first': 11,
        'last': None,
        'userID': user_id,
        **get_relay_flags(logged_in=False),
    }
    return _get_payload(
        doc_id="27545758055009868",
        friendly_name="BarcelonaProfileThreadsTabRefetchableDirectQuery",
        variables=json.dumps(variables)
    )