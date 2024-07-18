# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#BATCHING
def batch_data(data, token_limit=100000):
    """
    breaks the data into batches based on the specified token limit
    """
    batches_dict = {}
    count = 1
    batch = ""
    tokens = 0

    for key, value in data.items():
        item = json.dumps({key: value}, indent=2)
        if tokens + len(item) // 4 > token_limit:
            batches_dict[count] = batch
            count += 1; batch = item + ",\n"; tokens = 0
        else:
            tokens += len(item) // 4
            batch += item + ",\n"
    
    if batch != "":
        batches_dict[count] = batch

    return batches_dict


#ASSEMBLE MESSAGE
def assemble_message(batch_data):
    """
    Returns a list of messges ready to send to claude 
    """   
    instructions = """
    I Want you to merge all the base fields in the base structures I am about to send you.
    
    here is some key points to note:
    - the base value for "base" keys is a struct name
    - the base struct name will always map to another structure in the list of base structures
    - I want you to process the base structures by merging together the base fields
    - in the output only output the structures the way they appear in the input 
    - key point: the base structs will start with the FTz prefix... ignore this prefix please and search for the structure without the prefix.
    - for example if you encounter "FTzPubSubChannelDataNotify" its really a referenece to "PubSubChannelDataNotify" (this applies to all base structs)
    - its crucial that you maintain the correct field order when merging out the base fields
    - in the output the structures should have no base fields.
    - for each strucuture you output, dont wrap it in {}, just print the structname: {}, 
    - dont add space between the structures you processed and dont split arrays and maps to new lines please

    
    EXAMPLES
    1.
    "PubSubChannelInitialDataNotify": {
        "Base": "FTzPubSubChannelDataNotify"
    },
    should become:
    "PubSubChannelInitialDataNotify": {
        "Channel": "ETzSubscriptionChannelType",
        "Parameter": "?"
    },
    by referencing: 
    "PubSubChannelDataNotify": {
        "Base": "FTzErTozMessage",
        "Channel": "ETzSubscriptionChannelType",
        "Parameter": "?"
    },
    2.
    "ErTozMessageWithResultCode": {
        "Base": "FTzErTozMessage",
        "ResultCode": "ETzResultCodeType"
    },
    should become:
    "ErTozMessageWithResultCode": {
        "ResultCode": "ETzResultCodeType"
    },
    by referencing:
    "ErTozMessage": {
    "Base": "FTzTozMessage"
    },
     "TozMessage": {},
    3.
    "ErLoginServerInitialToyAuthenticateInfo": {
        "Base": "FTzErLoginServerInitialAuthenticateInfo",
        "Npsn": "s",
        "NpToken": "s",
        "NgsmToken": "s",
        "NpaCode": "s",
        "NexonSn": "q"
    },
    should become:
    "ErLoginServerInitialToyAuthenticateInfo": {
        "LocalAreaNetworkAddress": "s"
        "Market": "ETzMarketType",
        "AuthenticationKind": "ETzAuthenticationKindType",
        "OsKind": "ETzOsKindType",
        "OsVersion": "s",
        "DeviceModel": "s",
        "Adid": "s",
        "Idfv": "s",
        "CountryCode": "s",
        "Language": "s",
        "AppVersion": "s",
        "OsType": "ETzNxLogOsType",
        "OsName": "s",
        "Npsn": "s",
        "NpToken": "s",
        "NgsmToken": "s",
        "NpaCode": "s",
        "NexonSn": "q"
    },
    by referencing:
    "ErLoginServerInitialAuthenticateInfo": {
        "Base": "FTzErLoginServerAuthenticateInfo",
        "Market": "ETzMarketType",
        "AuthenticationKind": "ETzAuthenticationKindType",
        "OsKind": "ETzOsKindType",
        "OsVersion": "s",
        "DeviceModel": "s",
        "Adid": "s",
        "Idfv": "s",
        "CountryCode": "s",
        "Language": "s",
        "AppVersion": "s",
        "OsType": "ETzNxLogOsType",
        "OsName": "s"
    },
    "ErLoginServerAuthenticateInfo": {
        "Base": "FTzErServerAuthenticateInfo"
    },
    "ErServerAuthenticateInfo": {
        "Base": "FTzAuthenticateInfo",
        "LocalAreaNetworkAddress": "s"
    },
    "AuthenticateInfo": {},
        """

    legend = """  
    BASE STRUCTS LEGEND:

  "AuthenticateInfo": {},
  "PubSubChannelInitialDataNotify": {
    "Base": "FTzPubSubChannelDataNotify"
  },
  "RankingViewInfo": {},
  "HandshakeResult": {
    "Success": "?"
  },
  "StrongholdBattleInfo": {
    "Guid": "q",
    "StrongholdCuid": "I",
    "StrongholdBattleKind": "ETzStrongholdBattleKindType",
    "StartTime": "IQ",
    "BuildingStateInfos": {"I": "FTzStrongholdBattleBuildingStateInfo"},
    "DefenseInfos": {"ETzStrongholdBattleDeploymentKindType": "FTzStrongholdBattleDefenseGroupInfo"},
    "AttackInfos": {"ETzStrongholdBattleDeploymentKindType": "FTzStrongholdBattleAttackInfo"}
  },
  "CovenantRankingViewInfo": {
    "Base": "FTzRankingViewInfo",
    "Guid": "q",
    "OriginRealmCuid": "I",
    "Name": "s",
    "LeaderName": "s",
    "Level": "i",
    "MemberCount": "h",
    "MaxMemberCount": "h",
    "EmblemInfo": "FTzCovenantEmblemInfo",
    "CampCuid": "I",
    "OccupiedStrongholdCuids": ["I"],
    "MainHavenCuid": "I"
  },
  "ErTozMessageWithResultCode": {
    "Base": "FTzErTozMessage",
    "ResultCode": "ETzResultCodeType"
  },
  "BattalionCreateNotify": {
    "Base": "FTzErTozMessage",
    "BattalionInfo": "msg"
  },
  "BattalionSummaryInfo": {
    "BattalionGuid": "q",
    "CovenantGuid": "q",
    "CovenantName": "s",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "CreateDateTime": "IQ",
    "BattalionOptionInfo": "FTzBattalionOptionInfo",
    "BattalionLeaderInfo": "FTzBattalionMemberInfo",
    "AverageMemberLevel": "i",
    "MemberCount": "i",
    "BattalionLeaderLocationInfo": "FTzLocationInfo",
    "AssemblyLocationInfo": "FTzLocationInfo",
    "IsJoinable": "?"
  },
  "PubSubChannelUpdateDataNotify": {
    "Base": "FTzPubSubChannelDataNotify"
  },
  "BossSpawnInfo": {
    "SpawnerCuid": "I",
    "SpawnDateTime": "?",
    "ForceDespawnDateTime": "?"
  },
  "CrossRealmSeasonEntryUpdateDataNotify": {
    "Base": "FTzPubSubChannelUpdateDataNotify"
  },
  "PlayerRankingViewInfo": {
    "Base": "FTzRankingViewInfo",
    "Guid": "q",
    "Classe": "ETzClasseType",
    "Level": "i",
    "SlayingGrade": "h",
    "Name": "s",
    "CovenantGuid": "q",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "CovenantName": "s"
  },
  "SeamlessEntityInfo": {
    "EntityInfo": "msg",
    "PlacedDistrictCuid": "I",
    "PlacedZoneCuid": "I"
  },
  "BaseGameOptionInfo": {},
  "CovenantWatchInfo": {
    "TargetPlayerGuid": "q",
    "TotalKillCount": "i",
    "CovenantWatchKillingInfos": ["FTzCovenantWatchKillingInfo"],
    "CreateDateTime": "IQ"
  },
  "CovenantJoinedStrongholdBattleInfo": {
    "StrongholdCuid": "I",
    "StrongholdBattleGuid": "q",
    "DeploymentKind": "ETzStrongholdBattleDeploymentKindType",
    "BattalionGuid": "q"
  },
  "ItemAdditionalInfo": {},
  "RPCMessage": {
    "ReturnIndex": "i"
  },
  "PubSubChannelDataNotify": {
    "Base": "FTzErTozMessage",
    "Channel": "ETzSubscriptionChannelType",
    "Parameter": "?"
  },
  "BuffMoveAffectInfo": {
    "Base": "FTzBuffAffectInfo",
    "Destination_cm": "3f"
  },
  "SkillMoveAffectInfo": {
    "MoveDuration_msec": "i",
    "Destination_cm": "?",
    "InitialDirectionYaw_rad": "?",
    "InitialFacingEntityGuid": "?",
    "FinalDirectionYaw_rad": "?",
    "FinalFacingEntityGuid": "?"
  },
  "MerchandisePaymentInfo": {
    "TargetCuid": "I"
  },
  "ErTozInitializeMessage": {
    "Base": "FTzErTozMessage"
  },
  "PvpScoreRankingViewInfo": {
    "Base": "FTzRankingViewInfo",
    "PlayerGuid": "q",
    "Classe": "ETzClasseType",
    "Name": "s",
    "CovenantName": "s",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "PvpScore": "i",
    "AdditionalSourceInfo": "msg"
  },
  "BattalionMemberInfoSynchronizeNotify": {
    "Base": "FTzErTozMessage",
    "PlayerGuid": "q"
  },
  "FollowerReturnReasonAdditionalInfo": {},
  "SingleItemSelector": {
    "Base": "FTzItemSelector"
  },
  "SkillAffectInfo": {},
  "StrongholdBattleGroupInfo": {
    "CovenantVuid": "FTzVuid",
    "CovenantName": "s",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "CovenantCreateDateTime": "IQ",
    "BattalionGuid": "q",
    "DeploymentKind": "ETzStrongholdBattleDeploymentKindType",
    "AetherBoxCount": "i",
    "MaxAetherBoxCount": "i",
    "TacticalSkillBadgeCount": "i",
    "MaxTacticalSkillBadgeCount": "i",
    "NextResurrectTime": "IQ",
    "MemberCount": "i",
    "CreateDateTime": "IQ",
    "LivingTotemCuid": "I"
  },
  "BuildingWorkRequestInfo": {
    "BaseInfo": "msg"
  },
  "InGameNotificationInfo": {
    "Guid": "q",
    "InGameNotificationCategory": "ETzInGameNotificationCategoryType",
    "AdditionalCuidParams": ["I"],
    "AdditionalGuidParam": "q",
    "NotificationExpireDateTime": "?"
  },
  "CrossRealmSeasonEntryInitialDataNotify": {
    "Base": "FTzPubSubChannelInitialDataNotify"
  },
  "ErLoginServerInitialAuthenticateInfo": {
    "Base": "FTzErLoginServerAuthenticateInfo",
    "Market": "ETzMarketType",
    "AuthenticationKind": "ETzAuthenticationKindType",
    "OsKind": "ETzOsKindType",
    "OsVersion": "s",
    "DeviceModel": "s",
    "Adid": "s",
    "Idfv": "s",
    "CountryCode": "s",
    "Language": "s",
    "AppVersion": "s",
    "OsType": "ETzNxLogOsType",
    "OsName": "s"
  },
  "NpcOccupationScoreCovenantInfo": {
    "RealmCovenantId": "FTzRealmCovenantId",
    "MemberCounts": "i",
    "OccupationScore": "i",
    "FirstGainedScoreDateTime": "IQ"
  },
  "DividendResultInfo": {
    "CurrencyCuid": "I",
    "TotalDistributionAmount": "q"
  },
  "ItemUseParameterInfo": {},
  "SessionInitializeInfo": {},
  "ChatRequest": {
    "Base": "FTzErTozMessage",
    "ChatKind": "ETzChatKindType",
    "InfoToShare": "s",
    "Text": "s"
  },
  "MessageCacheElement": {
    "CacheTicks": "l"
  },
  "BattalionInfo": {
    "BattalionGuid": "q",
    "CovenantGuid": "q",
    "CovenantName": "s",
    "AllianceCovenantGuids": ["q"],
    "CovenantGrantedSkillCuids": ["I"],
    "CreateDateTime": "IQ",
    "BattalionOptionInfo": "FTzBattalionOptionInfo",
    "SquadInfos": ["FTzSquadInfo"],
    "MemberInfos": {"q": "FTzBattalionMemberInfo"},
    "AssemblyLocationInfo": "FTzLocationInfo",
    "CheckReadyExpireDateTime": "?",
    "IsJoinable": "?",
    "BattalionWarpCooldownExpireTime": "?"
  },
  "CovenantTradeGoodsInfo": {
    "Guid": "q",
    "ItemIndexWithCount": "msg",
    "SalesPrice": "q",
    "SellerInfo": "msg",
    "RegistrationDateTime": "IQ"
  },
  "ErServerSessionInitializeInfo": {
    "Base": "FTzSessionInitializeInfo",
    "UtcNow": "IQ"
  },
  "CharacterMoveToLocationParameterInfo": {
    "Destination_cm": "3f"
  },
  "ErLoginServerAuthenticateInfo": {
    "Base": "FTzErServerAuthenticateInfo"
  },
  "CovenantMemberAnniversaryPointInfo": {
    "CovenantMemberGuid": "q",
    "CovenantMemberName": "s",
    "UpdateTime": "IQ"
  },
  "PvpRecordPlayerInfo": {
    "Base": "FTzPvpRecordCharacterInfo",
    "Name": "s",
    "Classe": "ETzClasseType",
    "RealmCuid": "I",
    "PvpScore": "q",
    "PvpScoreDelta": "q"
  },
  "CastAffectSourceInfo": {
    "Base": "FTzAffectSourceInfo"
  },
  "MountCallingRequest": {
    "Base": "FTzErTozMessage",
    "PlayerLocation_cm": "3f"
  },
  "MailStrongholdBattleLayoutInfo": {
    "Base": "FTzMailLayoutInfo",
    "StrongholdCuid": "I"
  },
  "EntitySynchronizeMessage": {
    "Base": "FTzErTozMessage",
    "EntityGuid": "q"
  },
  "StackableItemQuickSlotDetailInfo": {
    "Base": "FTzItemQuickSlotDetailInfo"
  },
  "TozMessage": {},
  "StrongholdBattleAttackSiegeWeaponSlotInfo": {
    "SlotIndex": "h",
    "SiegeWeaponItemCuid": "I",
    "SiegeWeaponGuid": "q",
    "TargetSpawnerCuid": "I"
  },
  "CovenantTradeGoodsSalesInfo": {
    "Base": "FTzCovenantTradeGoodsInfo",
    "SalesState": "ETzCovenantTradeSalesStateType",
    "NetProfit": "q"
  },
  "MonsterBookNodeStateInfo": {
    "NodeCuid": "I",
    "AnalysisColorCuid": "I",
    "AnalysisRewardStatCuid": "I",
    "IsAnalysisLocked": "?"
  },
  "CharacterInfo": {
    "Base": "FTzEntityInfo",
    "CharacterState": "ETzCharacterStateType",
    "CharacterPublicStatsInfo": "msg",
    "BuffInfos": ["FTzBuffInfo"],
    "CharacterMoveInfo": "msg",
    "FocusTargetGuid": "q",
    "AttackTargetGuid": "q",
    "FinishableExpireDateTime": "?",
    "ParticipatingContentsGuids": ["q"],
    "IsHarmfulSkillTargetableInAnyFactionRelation": "?",
    "StrongholdBattleGuid": "q"
  },
  "ItemIndexWithCount": {
    "Base": "FTzItemIndex",
    "Count": "q"
  },
  "MountStateInfo": {},
  "RankingAdditionalSourceInfo": {},
  "PartySynchronizeMemberNotify": {
    "Base": "FTzErTozMessage",
    "PlayerGuid": "q"
  },
  "CharacterRotateTowardsLocationInfo": {
    "Base": "FTzCharacterRotateInfo",
    "TargetLocation_cm": "3f"
  },
  "CharacterMoveInfo": {
    "Location_cm": "3f",
    "ServerUtcNow": "IQ",
    "DelayForOthersDuration_msec": "f"
  },
  "MultipleItemSelector": {
    "Base": "FTzItemSelector"
  },
  "SkillStatsAffectInfo": {
    "HealthPointsDelta": "i",
    "ManaPointsDelta": "i"
  },
  "StackableItemInfo": {
    "Base": "FTzItemInfo",
    "StackCount": "q"
  },
  "EntityInfo": {
    "Entity": "ETzEntityType",
    "Guid": "q",
    "RealmCuid": "I",
    "LocationInfo": "FTzLocationInfo",
    "Faction": "ETzFactionType",
    "RealmCovenantId": "FTzRealmCovenantId",
    "CovenantName": "s",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "AffiliatedStrongholdCuid": "I"
  },
  "FollowerKillingInfo": {
    "KillerEntityName": "s",
    "KillerCovenantName": "s",
    "KillingLocationInfo": "FTzLocationInfo"
  },
  "DividendInfo": {
    "CurrencyCuid": "I",
    "DistributionAmount": "q"
  },
  "PvpRecordAttackerPlayerInfo": {
    "Base": "FTzPvpRecordPlayerInfo",
    "Damage": "q",
    "AttackerKind": "ETzPvpRecordAttackerKindType",
    "LastAttackDateTime": "IQ"
  },
  "CharacterStatsInfo": {},
  "MarketGoodsSummaryQueryInfo": {
    "MarketKind": "ETzMarketKindType",
    "MainGroupCuid": "I",
    "SubGroupCuid": "I",
    "ItemCuid": "I"
  },
  "ChatInfo": {
    "ChatKind": "ETzChatKindType",
    "OriginRealmCuid": "I",
    "SenderCharacterName": "s",
    "SenderClasse": "ETzClasseType",
    "SenderLevel": "i",
    "SenderSlayingGrade": "h",
    "SenderPlayerExperiencePointsRanking": "?",
    "SenderFieldUid": "FTzFieldUid",
    "SenderGuid": "q",
    "HighestOccupiedStrongholdGrade": "ETzStrongholdGradeType",
    "InfoToShare": "s",
    "Text": "s",
    "HarmfulTextKind": "ETzHarmfulTextKindType",
    "RegisterDateTime": "IQ"
  },
  "MailBuildingWorkLayoutInfo": {
    "Base": "FTzMailLayoutInfo",
    "HavenCuid": "I",
    "BuildingCuid": "I",
    "BuildingWorkKind": "ETzBuildingWorkKindType"
  },
  "FavorMissionInfo": {
    "Vuid": "FTzVuid",
    "FavorVuid": "FTzVuid",
    "HuntingSiteCuidList": ["I"],
    "TargetCuidList": ["I"],
    "LevelOfTargetNpc": "i",
    "ClanCuid": "I"
  },
  "AchievementInfo": {
    "AchievementCuid": "I",
    "MissionProgressCounts": ["q"],
    "AccomplishDateTime": "?",
    "IsRewarded": "?"
  },
  "MailFollowerWorkLayoutInfo": {
    "Base": "FTzMailLayoutInfo",
    "HavenCuid": "I",
    "GainedCovenantExperiencePoints": "q",
    "GainedFollowerExperiencePoints": "q"
  },
  "ItemQuickSlotDetailInfo": {
    "Base": "FTzQuickSlotDetailInfo",
    "ItemCuid": "I"
  },
  "DistrictFavorBossInfo": {
    "BossChaseGauge": "i",
    "IsFavorBossActivated": "?"
  },
  "CovenantSynchronizeMemberNotify": {
    "Base": "FTzErTozMessage",
    "PlayerGuid": "q"
  },
  "PvpRecordCharacterInfo": {
    "Guid": "q",
    "CrossRealmSeasonCuid": "I",
    "Role": "ETzPvpRecordCharacterRoleType"
  },
  "BattalionJoinMemberNotify": {
    "Base": "FTzErTozMessage",
    "SquadOrder": "i",
    "SquadMemberOrder": "i",
    "MemberInfo": "FTzBattalionMemberInfo"
  },
  "ItemInfo": {
    "Guid": "q",
    "Cuid": "I",
    "IsBound": "?",
    "IsStorable": "?",
    "ExpireDateTime": "?",
    "AcquiredDateTime": "IQ",
    "IsLocked": "?"
  },
  "ServerDrivenPlayRewardInfo": {
    "GainedExperiencePoints": "q",
    "GainedSpiritualBondPower": "q",
    "GainedCurrencies": {"I": "q"},
    "GainedItemInfos": ["FTzGainedItemInfo"]
  },
  "AffectSourceInfo": {
    "Cuid": "I",
    "SourceEntityGuid": "q"
  },
  "MountDeboardingInfo": {
    "Base": "FTzMountStateInfo",
    "MountDeboardReason": "ETzMountDeboardReasonType",
    "IsImmediateMountDespawn": "?",
    "MountDespawnLocation_cm": "3f"
  },
  "FocusRequest": {
    "Base": "FTzErTozMessage",
    "FocusTargetGuid": "q"
  },
  "CharacterPublicStatsInfo": {
    "Base": "FTzCharacterStatsInfo",
    "Level": "i",
    "HealthPoints": "q",
    "MaxHealthPoints": "q",
    "WalkSpeed_cmpsec": "h",
    "WalkAngularSpeed_radpsec": "f",
    "RunSpeed_cmpsec": "h",
    "RunAngularSpeed_radpsec": "f"
  },
  "SharedTargetCharacterInfo": {
    "Cuid": "I",
    "Entity": "ETzEntityType",
    "Guid": "q",
    "CovenantVuid": "FTzVuid"
  },
  "ErLoginServerInitialDevAuthenticateInfo": {
    "Base": "FTzErLoginServerInitialAuthenticateInfo",
    "UserName": "s"
  },
  "PvpRecordNpcInfo": {
    "Base": "FTzPvpRecordCharacterInfo",
    "Cuid": "I"
  },
  "ServerDrivenPlayStateInfo": {},
  "CovenantDiplomacyAdditionalInfo": {},
  "PvpRankingAdditionalSourceInfo": {
    "Base": "FTzRankingAdditionalSourceInfo",
    "DeadCount": "i",
    "KillCount": "i",
    "AssistCount": "i"
  },
  "CovenantHistoryInfo": {
    "Guid": "q",
    "CreateDateTime": "IQ"
  },
  "SendChatMessageRequest": {
    "Base": "FTzErTozMessage",
    "ChatKind": "ETzChatKindType",
    "InfoToShare": "s",
    "Text": "s"
  },
  "ItemSelector": {},
  "ErTozMessage": {
    "Base": "FTzTozMessage"
  },
  "StrongholdBattleStatisticsEventInfo": {
    "EventInvokerCharacterGuid": "q"
  },
  "DoodadInfo": {
    "Base": "FTzEntityInfo",
    "DoodadCuid": "I",
    "SpawnerCuid": "I"
  },
  "FavorInfo": {
    "Vuid": "FTzVuid",
    "FavorTemplateCuid": "I",
    "TerritoryCuid": "I",
    "FavorAcceptedStrongholdCuid": "I",
    "FavorRandomRewardCuidCandidates": ["I"]
  },
  "ErFrontServerAuthenticateInfo": {
    "Base": "FTzErServerAuthenticateInfo"
  },
  "SkillTargetingInfo": {},
  "ErLoginServerInitialToyAuthenticateInfo": {
    "Base": "FTzErLoginServerInitialAuthenticateInfo",
    "Npsn": "s",
    "NpToken": "s",
    "NgsmToken": "s",
    "NpaCode": "s",
    "NexonSn": "q"
  },
  "AttackTargetRequest": {
    "Base": "FTzErTozMessage",
    "AttackTargetGuid": "q"
  },
  "BaseInfo": {
    "Token": "s"
  },
  "ErServerAuthenticateInfo": {
    "Base": "FTzAuthenticateInfo",
    "LocalAreaNetworkAddress": "s"
  },
  "ItemIndex": {
    "Base": "FTzMultipleItemSelector",
    "ItemCuid": "I",
    "IsBound": "?",
    "IsStorable": "?",
    "IsEroded": "?",
    "ExpireDateTime": "?",
    "GearQuality": "ETzGearQualityType"
  },
  "AcquireSourceAdditionalParameter": {},
  "HavenOccupancyInfo": {
    "Cuid": "I",
    "HavenOperationInfo": "FTzHavenOperationInfo"
  },
  "InteractableDoodadInfo": {
    "Base": "FTzDoodadInfo",
    "RemainingInteractionCompleteCount": "i"
  },
  "NpcOccupationCovenantInfo": {
    "RealmCovenantId": "FTzRealmCovenantId",
    "OccupationDateTime": "IQ",
    "OccupationScore": "i"
  },
  "StrongholdBattleAttackPhaseStartNotify": {
    "Base": "FTzErTozMessage",
    "StrongholdCuid": "I",
    "AttackGroupDeploymentKind": "ETzStrongholdBattleDeploymentKindType",
    "BattalionMemberStatisticsInfos": ["FTzStrongholdBattleCovenantBattalionMemberStatisticsInfo"]
  },
  "AchievementSourceInfo": {},
  "DistrictInfo": {
    "Cuid": "I"
  },
  "CharacterMoveToInfo": {
    "Base": "FTzCharacterMoveInfo",
    "CurrentFacingDirectionYaw_rad": "f",
    "MoveKind": "ETzMoveKindType"
  },
  "CharacterRotateInfo": {
    "Base": "FTzCharacterMoveInfo",
    "Duration_msec": "i",
    "IsClockwise": "?",
    "MoveKind": "ETzMoveKindType"
  },
  "MailLayoutInfo": {
    "MailLayoutKind": "ETzMailLayoutKindType"
  },
  "InstanceEventActionStartNotify": {
    "Base": "FTzErTozMessage",
    "ActionCuid": "I"
  },
  "QuickSlotDetailInfo": {},
  "BuffAffectInfo": {},
  "ChatRoomRecordsInitializationInfo": {
    "ChatKind": "ETzChatKindType",
    "ChatRoomGuid": "q",
    "ChannelIndex": "H",
    "ChatRecordsMetaData": "FTzChatRecordsMetaData",
    "FirstRecordIndex": "q",
    "LastRecordIndex": "q",
    "ChatMessageInfos": ["FTzChatMessageInfo"]
  },
  "TriggerWorldActionInfo": {},
  "CharacterPrivateStatsInfo": {
    "Base": "FTzCharacterStatsInfo",
    "ExperiencePoints": "q",
    "HealthPointsRegenerationOutOfCombatUnit": "q",
    "HealthPointsRegenerationInCombatUnit": "q",
    "ManaPoints": "q",
    "MaxManaPoints": "q",
    "ManaPointsRegenerationOutOfCombatUnit": "q",
    "ManaPointsRegenerationInCombatUnit": "q",
    "Potential": "i",
    "OffensivePower": "i",
    "AdditionalMeleeOffensivePower": "i",
    "AdditionalRangedOffensivePower": "i",
    "AdditionalMagicOffensivePower": "i",
    "WeaponMinDamage": "i",
    "WeaponMaxDamage": "i",
    "Hit": "i",
    "MeleeHit": "i",
    "RangedHit": "i",
    "MagicHit": "i",
    "SkillHit": "i",
    "StunHitRatio_pe4": "i",
    "SilenceHitRatio_pe4": "i",
    "BlindHitRatio_pe4": "i",
    "OverlayDebuffHitRatio_pe4": "i",
    "PierceRatio_pe4": "i",
    "CriticalRatio_pe4": "i",
    "AdditionalWeaponDamageAmount": "i",
    "AdditionalWeaponDamageRatio_pe4": "i",
    "CriticalDamageIncreaseRatio_pe4": "i",
    "SkillDamageRatio_pe4": "i",
    "AdditionalMeleeDamageAmount": "i",
    "AdditionalMeleeOffensivePowerRatio_pe4": "i",
    "AdditionalRangedDamageAmount": "i",
    "AdditionalRangedOffensivePowerRatio_pe4": "i",
    "AdditionalMagicDamageAmount": "i",
    "AdditionalMagicOffensivePowerRatio_pe4": "i",
    "AdditionalFireDamageAmount": "i",
    "AdditionalFireDamageRatio_pe4": "i",
    "AdditionalWaterDamageAmount": "i",
    "AdditionalWaterDamageRatio_pe4": "i",
    "AdditionalEarthDamageAmount": "i",
    "AdditionalEarthDamageRatio_pe4": "i",
    "AdditionalWindDamageAmount": "i",
    "AdditionalWindDamageRatio_pe4": "i",
    "AdditionalHolyDamageAmount": "i",
    "AdditionalHolyDamageRatio_pe4": "i",
    "AdditionalDarkDamageAmount": "i",
    "AdditionalDarkDamageRatio_pe4": "i",
    "AdditionalDivineDamageAmount": "i",
    "AdditionalDivineDamageRatio_pe4": "i",
    "AdditionalHumanoidDamageAmount": "i",
    "AdditionalHumanoidDamageRatio_pe4": "i",
    "AdditionalElvenDamageAmount": "i",
    "AdditionalElvenDamageRatio_pe4": "i",
    "AdditionalEntangledDamageAmount": "i",
    "AdditionalEntangledDamageRatio_pe4": "i",
    "AdditionalBeastDamageAmount": "i",
    "AdditionalBeastDamageRatio_pe4": "i",
    "AdditionalAbyssalDamageAmount": "i",
    "AdditionalAbyssalDamageRatio_pe4": "i",
    "AdditionalSiegeWeaponDamageAmount": "i",
    "AdditionalSiegeWeaponDamageRatio_pe4": "i",
    "AdditionalBossDamageAmount": "i",
    "AdditionalBossDamageRatio_pe4": "i",
    "AdditionalCriticalDamageAmount": "i",
    "AdditionalDamageAmount": "i",
    "PierceDamageAmount": "i",
    "DefensivePower": "i",
    "SkillDefensivePower": "i",
    "Dodge": "i",
    "MeleeDodge": "i",
    "RangedDodge": "i",
    "MagicDodge": "i",
    "SkillDodge": "i",
    "StunResistRatio_pe4": "i",
    "SilenceResistRatio_pe4": "i",
    "BlindResistRatio_pe4": "i",
    "UniversalDebuffResistAmount": "i",
    "OverlayDebuffResistRatio_pe4": "i",
    "OverlayDebuffDecreaseRatio_pe4": "i",
    "BlockRatio_pe4": "i",
    "CriticalResistRatio_pe4": "i",
    "AbsorbAdditionalWeaponDamageAmount": "i",
    "AbsorbAdditionalWeaponDamageRatio_pe4": "i",
    "CriticalDamageReduceRatio_pe4": "i",
    "AbsorbSkillDamageRatio_pe4": "i",
    "AbsorbAdditionalMeleeDamageAmount": "i",
    "AbsorbAdditionalMeleeDamageRatio_pe4": "i",
    "AbsorbAdditionalRangedDamageAmount": "i",
    "AbsorbAdditionalRangedDamageRatio_pe4": "i",
    "AbsorbAdditionalMagicDamageAmount": "i",
    "AbsorbAdditionalMagicDamageRatio_pe4": "i",
    "AbsorbAdditionalFireDamageAmount": "i",
    "AbsorbAdditionalFireDamageRatio_pe4": "i",
    "AbsorbAdditionalWaterDamageAmount": "i",
    "AbsorbAdditionalWaterDamageRatio_pe4": "i",
    "AbsorbAdditionalEarthDamageAmount": "i",
    "AbsorbAdditionalEarthDamageRatio_pe4": "i",
    "AbsorbAdditionalWindDamageAmount": "i",
    "AbsorbAdditionalWindDamageRatio_pe4": "i",
    "AbsorbAdditionalHolyDamageAmount": "i",
    "AbsorbAdditionalHolyDamageRatio_pe4": "i",
    "AbsorbAdditionalDarkDamageAmount": "i",
    "AbsorbAdditionalDarkDamageRatio_pe4": "i",
    "AbsorbAdditionalCriticalDamageAmount": "i",
    "AbsorbAllKindOfDamageAmount": "i",
    "IgnoreAbsorbAllKindOfDamageAmount": "i",
    "BasicAttackSpeedIncrease": "i",
    "NonBasicAttackSpeedIncrease": "i",
    "SkillCooldownDurationDecreaseRatio_pe4": "i",
    "SomaHit": "i",
    "SomaSkillHit": "i",
    "SomaMeleeHit": "i",
    "SomaRangedHit": "i",
    "SomaMagicHit": "i",
    "SomaSkillDamageRatio_pe4": "i",
    "SomaAdditionalCriticalDamageAmount": "i",
    "SomaCriticalDamageIncreaseRatio_pe4": "i",
    "SomaAdditionalBossDamageAmount": "i",
    "SomaAdditionalBossDamageRatio_pe4": "i",
    "SomaAdditionalMeleeDamageAmount": "i",
    "SomaAdditionalMeleeOffensivePowerRatio_pe4": "i",
    "SomaAdditionalRangedDamageAmount": "i",
    "SomaAdditionalRangedOffensivePowerRatio_pe4": "i",
    "SomaAdditionalMagicDamageAmount": "i",
    "SomaAdditionalMagicOffensivePowerRatio_pe4": "i",
    "SomaWeaponDamageAmount": "i",
    "SomaWeaponDamageRatio_pe4": "i",
    "SomaAdditionalDamageAmount": "i",
    "SomaPvpDamageAmount": "i",
    "SomaAdditionalPvpDamageRatio_pe4": "i",
    "ExpeditionDamageRatio_pe4": "i",
    "ExpeditionNormalHitIncreaseRatio_pe4": "i",
    "ExpeditionSkillHitIncreaseRatio_pe4": "i",
    "ExpeditionAbsorbAllKindOfDamageAmount": "i",
    "ImmobilizeHitRatio_pe4": "i",
    "ImmobilizeResistRatio_pe4": "i",
    "DownHitRatio_pe4": "i",
    "DownResistRatio_pe4": "i",
    "SleepHitRatio_pe4": "i",
    "SleepResistRatio_pe4": "i",
    "FreezingHitRatio_pe4": "i",
    "FreezingResistRatio_pe4": "i",
    "DisengageHitRatio_pe4": "i",
    "TauntResistRatio_pe4": "i",
    "TauntHitRatio_pe4": "i",
    "DisengageResistRatio_pe4": "i",
    "CrowdControlDurationIncreaseAmount": "i",
    "CrowdControlDurationDecreaseAmount": "i",
    "DebuffDurationIncreaseAmount": "i",
    "DebuffDurationDecreaseAmount": "i",
    "AdditionalStunDamageAmount": "i",
    "AdditionalSilenceDamageAmount": "i",
    "AdditionalImmobilizeDamageAmount": "i",
    "AdditionalDownDamageAmount": "i",
    "AdditionalDamagePeriodicDamageAmount": "i",
    "AdditionalBlindDamageAmount": "i",
    "AdditionalFreezingDamageAmount": "i",
    "AdditionalBuildingDamageAmount": "i",
    "TotalNormalHitRatio_pe4": "i",
    "TotalNormalDodgeRatio_pe4": "i",
    "TotalSkillHitRatio_pe4": "i",
    "TotalSkillDodgeRatio_pe4": "i",
    "TotalAdditionalDamageRatio_pe4": "i",
    "TotalAbsorbDamageRatio_pe4": "i",
    "AdditionalNonBossNpcDamageAmount": "i",
    "AdditionalNonBossNpcDamageRatio_pe4": "i",
    "NonBossNpcHit": "i",
    "NonBossNpcDodge": "i",
    "KnockbackHitRatio_pe4": "i",
    "KnockbackResistRatio_pe4": "i",
    "PullHitRatio_pe4": "i",
    "PullResistRatio_pe4": "i",
    "HitImmobilizeHitRatio_pe4": "i",
    "HitImmobilizeResistRatio_pe4": "i",
    "AbsorbPeriodicLossRatio_pe4": "i",
    "AdditionalPvpDamageAmount": "i",
    "AdditionalPvpDamageRatio_pe4": "i",
    "AbsorbAdditionalPvpDamageAmount": "i",
    "AbsorbAdditionalPvpDamageRatio_pe4": "i",
    "PvpHit": "i",
    "PvpDodge": "i",
    "AdditionalNonBossNpcOffensivePower": "i",
    "AdditionalBossOffensivePower": "i",
    "AdditionalNonBossNpcDefensivePower": "i",
    "AdditionalBossDefensivePower": "i",
    "AbsorbAdditionalNonBossNpcDamageAmount": "i",
    "AbsorbAdditionalBossDamageAmount": "i",
    "AbsorbAdditionalMeleeOffensivePower": "i",
    "AbsorbAdditionalRangedOffensivePower": "i",
    "AbsorbAdditionalMagicOffensivePower": "i",
    "AdditionalMeleeDefensivePower": "i",
    "AdditionalRangedDefensivePower": "i",
    "AdditionalMagicDefensivePower": "i",
    "AdditionalHealTargetPowerRatio_pe4": "i",
    "AbsorbBlockDamageAmount": "i",
    "AdditionalMeleeTargetOffensivePower": "i",
    "AdditionalRangedTargetOffensivePower": "i",
    "AdditionalMagicTargetOffensivePower": "i",
    "GlancingBlowHit": "i",
    "GlancingBlowDamageRatio_pe2": "i"
  },
  "DropParameter": {
    "Base": "FTzAcquireSourceAdditionalParameter",
    "NpcCuid": "I"
  },
  "CovenantDiplomacyInfo": {
    "RequestCovenantGuid": "q",
    "ResponseCovenantGuid": "q",
    "CovenantDiplomacyState": "ETzCovenantDiplomacyStateType",
    "CreateDateTime": "IQ",
    "CovenantDiplomacyAdditionalInfo": "msg"
  },
  "ErGameServerAuthenticateInfo": {
    "Base": "FTzErServerAuthenticateInfo",
    "AuthenticateKey": "i"
  },
  "MarketGoodsInfo": {
    "GoodsGuid": "q",
    "RealmCuid": "I",
    "MarketKind": "ETzMarketKindType",
    "SellPlayerName": "s",
    "ItemCuid": "I",
    "IsStorable": "?",
    "ItemAdditionalInfo": "msg",
    "ItemStackCount": "i",
    "CurrencyCuid": "I",
    "CurrencyAmount": "q",
    "ExpireDateTime": "IQ",
    "Index": "?",
    "UpdateDateTime": "IQ"
  },
  "BattalionPublicSummaryInfo": {
    "BattalionGuid": "q",
    "CovenantGuid": "q",
    "CovenantName": "s",
    "CovenantEmblemInfo": "FTzCovenantEmblemInfo",
    "CreateDateTime": "IQ",
    "BattalionLeaderPlayerName": "s",
    "MemberCount": "i"
  } """

    
    message = [
        {"role": "user", "content": instructions},
        {"role": "assistant", "content": "Ok Got it! Send me the structures!"},
        {"role": "user", "content": batch_data},
        # {"role": "assistant", "content": "Noted! now send me the batch of structures that you want me to merge the base field for."},
        # {"role": "user", "content": batch_data}
    ]
    return message

   
#SEND MESSAGE
def send_message(message):
    """
    sends message to claude and return the response
    """
    import anthropic
    client = anthropic.Anthropic(
        api_key="",
        default_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"})
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0.7,
        system="Your world-class reverse engineer with a specialization in simplifying parsing structures",
        messages = message,
    )
    return response


#SAVE RESPONSE
def save_response(content, file):
    """
    append to output file
    """
    with open(file, 'a') as f:
        f.write("\n")
        f.write(content)
    
    return True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


import json

INPUT_FILEPATH = 'base_structs.json'
OUTPUT_FILEPATH = '_base_structs_merged.json'
with open(INPUT_FILEPATH, 'r') as file:
    data = json.load(file)


def main():
    """
    make claude clean the structures and save the results
    """
    batches = batch_data(data, token_limit=4000)
    print(len(batches))
    for key, value in batches.items():
        print("\n-----------------------")
        print(f"Processing batch: {key}...")

        message = assemble_message(value)
        response = send_message(message)

        saved = save_response(response.content[0].text, OUTPUT_FILEPATH)
        if not saved:
            print(f"Error saving batch{key}")

        if response.stop_reason != "end_turn":
            print(f"Error encountered while processing batch {key}, {response.stop_reason}, {response.usage.input_tokens}, {response.usage.output_tokens}")
            break
        else:
            print(f"SUCCESS! \nAppended Claude's response to \"{OUTPUT_FILEPATH}\" for batch: {key}")
            print(f"Input tokens: {response.usage.input_tokens}")
            print(f"Output tokens: {response.usage.output_tokens}")
    
    print("\n-----------")
    print(f"FINISHED")
    print(f"PROCESSED ALL {len(batches)} to {OUTPUT_FILEPATH}")




main()
