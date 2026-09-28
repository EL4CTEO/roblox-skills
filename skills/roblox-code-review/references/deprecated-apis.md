# Deprecated and superseded Roblox APIs (engine reference, Studio 0.740, September 2026)

"Superseded" members still work but have a documented replacement — treat them as deprecated in new
code. Search this file for the member you're looking at. Camel-case aliases (`:findFirstChild`,
`:remove`, `.className`, ...) are all deprecated in favor of their PascalCase versions.

## Globals and libraries

| Deprecated | Use |
| --- | --- |
| `wait()` / `spawn()` / `delay()` | `task.wait()` / `task.spawn()` / `task.delay()` |
| `ypcall`, `elapsedTime`, `version`, `printidentity`, `stats()` | `pcall`, `os.clock`/`time()`, — , — , `game:GetService("Stats")` |
| `getfenv` / `setfenv` | nothing (disables optimizations) |
| `table.getn`, `table.foreach`, `table.foreachi` | `#t`, `for k, v in t do` |
| `Ray.new` + `FindPartOnRay*` | `workspace:Raycast(origin, direction, RaycastParams)` |
| `Region3` + `FindPartsInRegion3*`, `IsRegion3Empty*` | `workspace:GetPartBoundsInBox(cframe, size, OverlapParams)` |

## Players and characters

| Deprecated | Use |
| --- | --- |
| `Player:LoadCharacter()` | `Player:LoadCharacterAsync()` |
| `Player:LoadCharacterWithHumanoidDescription()` | `LoadCharacterWithHumanoidDescriptionAsync()` |
| `Player:LoadCharacterAppearance()`, `Player.CharacterAppearance`, `Players:GetCharacterAppearanceAsync()` | `HumanoidDescription` APIs |
| `Player:GetRankInGroup(Async)`, `Player:GetRoleInGroup(Async)` | `GroupService:GetRolesInGroupAsync()` |
| `Player:IsInGroup()` | `Player:IsInGroupAsync()` |
| `Player:IsFriendsWith()`, `IsBestFriendsWith()` | `Player:IsFriendsWithAsync()` |
| `Player:GetFriendsOnline()` | `Player:GetFriendsOnlineAsync()` |
| `Player.MembershipType` | `Player.HasRobloxSubscription` |
| `Player:Save*/Load*`, `DataReady`, `WaitForDataReady`, `DataComplexity` | `DataStoreService` |
| `Players.NumPlayers` | `#Players:GetPlayers()` |
| `Players:GetHumanoidDescriptionFromUserId/OutfitId()` | `...Async()` variants |
| `Players:CreateHumanoidModelFromDescription/UserId()` | `...Async()` variants |
| `Humanoid:LoadAnimation()`, `AnimationController:LoadAnimation()` | `Animator:LoadAnimation()` |
| `Humanoid:ApplyDescription()` / `ApplyDescriptionReset()` / `PlayEmote()` | `...Async()` variants |
| `Humanoid:*Status*` (RbxStatus), `Humanoid.Torso/LeftLeg/RightLeg` (R6-only) | attributes/tags; R15 body parts |
| `AnimationTrack.KeyframeReached` | `AnimationTrack:GetMarkerReachedSignal(name)` |
| `KeyframeSequenceProvider:GetKeyframeSequence*`, `AnimationClipProvider:GetAnimationClip*` | `AnimationClipProvider:GetAnimationClipAsync()` |
| `PoseBase.Weight`, `Pose.MaskWeight` | `AnimationTrack:AdjustWeight()` |

## Physics and parts

| Deprecated | Use |
| --- | --- |
| `BodyVelocity`, `BodyPosition`, `BodyGyro`, `BodyForce`, `BodyThrust`, `BodyAngularVelocity`, `RocketPropulsion` | `LinearVelocity`, `AlignPosition`, `AlignOrientation`, `VectorForce`, `AngularVelocity`, `LineForce` |
| `BasePart.Velocity` / `RotVelocity` | `AssemblyLinearVelocity` / `AssemblyAngularVelocity` (or `ApplyImpulse`) |
| `BasePart.Friction/Elasticity/SpecificGravity` | `CustomPhysicalProperties` |
| `BasePart:MakeJoints/BreakJoints`, `Model:MakeJoints`, surface joints (`Glue`, `Snap`, `Rotate*`, `Motor`, `ManualWeld`), `JointsService` | `WeldConstraint`, `HingeConstraint`, `GetJoints()` + `Destroy()` |
| `BasePart:GetRenderCFrame()` | `BasePart.CFrame` |
| `BasePart.StoppedTouching`, `LocalSimulationTouched` | `TouchEnded`, `Touched` |
| `PhysicsService:CreateCollisionGroup/RemoveCollisionGroup/GetCollisionGroups` | `workspace:RegisterCollisionGroup/UnregisterCollisionGroup/GetRegisteredCollisionGroups` |
| `PhysicsService:RegisterCollisionGroup`, `CollisionGroupSetCollidable`, `CollisionGroupsAreCollidable`, `IsCollisionGroupRegistered`, `RenameCollisionGroup`, `UnregisterCollisionGroup`, `GetMaxCollisionGroups` (superseded) | same methods on `workspace` (WorldRoot) |
| `PhysicsService:SetPartCollisionGroup`, `GetCollisionGroupId/Name`, `CollisionGroupContainsPart`, `BasePart.CollisionGroupId` | `BasePart.CollisionGroup` (string) |
| `Model:SetPrimaryPartCFrame()` / `GetPrimaryPartCFrame()` | `Model:PivotTo()` / `Model:GetPivot()` |
| `Model:GetModelCFrame()` / `GetModelSize()` | `GetPivot()`/`GetBoundingBox()` / `GetExtentsSize()` |
| `AlignOrientation.PrimaryAxisOnly` | `AlignOrientation.AlignType` |
| `Attachment.Rotation/WorldRotation`, `Get/SetAxis`, `Get/SetSecondaryAxis` | `Orientation`/`WorldOrientation`, `Axis`/`SecondaryAxis` properties / `CFrame` |
| `TorsionSpringConstraint.LimitEnabled` | `LimitsEnabled` |
| `VehicleSeat.Steer` / `Throttle` | `SteerFloat` / `ThrottleFloat` |
| `SkateboardPlatform`, `Flag`, `FlagStand` | custom systems |
| `FormFactorPart.FormFactor` | `Size` directly |

## Workspace, world, rendering

| Deprecated | Use |
| --- | --- |
| `Workspace.FilteringEnabled` | nothing (always on) |
| `game.Workspace`, `game.lighting` | `workspace`, `game:GetService("Lighting")` |
| `Lighting.Technology` (superseded) | `Lighting.LightingStyle` + `PrioritizeLightingQuality` |
| `Lighting.Outlines`, `ShadowColor`, `GetMoonPhase` | nothing |
| `Decal.Texture`, `Decal.TextureContent` (superseded) | `Decal.ColorMapContent` |
| `Decal.Shiny/Specular` | `SurfaceAppearance` / materials |
| `Terrain:SetCell/GetCell/SetCells/AutowedgeCell(s)/GetWaterCell/SetWaterCell`, `ConvertToSmooth`, `IsSmooth` | `FillBlock/FillBall/ReadVoxels/WriteVoxels` |
| `Sparkles.Color`, `ParticleEmitter.VelocitySpread`, `SelectionBox/Sphere.SurfaceColor`, `GuiBase3d.Color` | `SparkleColor`, `SpreadAngle`, `SurfaceColor3`, `Color3` |
| `Camera.CoordinateFrame`, `Camera:Interpolate`, `InterpolationFinished`, `SetRoll/GetRoll`, `PanUnits/TiltUnits`, `SetCameraPanMode` | `Camera.CFrame`, `TweenService`, CFrame math |
| `Hint`, `Message` | `TextLabel` in a `ScreenGui` |
| `Hat` | `Accessory` |
| `Skin` | `BodyColors` |
| `HopperBin`, `Hopper` | `Tool`, `StarterPack` |
| `FloorWire`, `SelectionPartLasso`, `SelectionPointLasso` | `Beam` |
| `CustomEvent`, `CustomEventReceiver` | `BindableEvent` (or a Luau signal module) |
| `IntConstrainedValue`, `DoubleConstrainedValue` | `IntValue`/`NumberValue` + `math.clamp`, or attributes |
| `Debris.MaxItems` | nothing |
| `Instance:Remove()` | `Instance:Destroy()` / `Parent = nil` |
| `Instance.RobloxLocked` | nothing |
| `DataModel.OnClose` | `game:BindToClose()` |
| `DataModel.VIPServerId/VIPServerOwnerId` | `PrivateServerId` / `PrivateServerOwnerId` |
| `DataModel:GetRemoteBuildMode()` | `RunService:IsServer()` |
| `DataModel.ItemChanged` | `Instance.Changed` / `GetPropertyChangedSignal` |
| `BaseScript.LinkedSource`, `ModuleScript.LinkedSource` | Packages |
| `CollectionService.ItemAdded/ItemRemoved`, `GetCollection` | `GetInstanceAddedSignal/GetInstanceRemovedSignal`, `GetTagged` |

## UI and input

| Deprecated | Use |
| --- | --- |
| `GuiObject:TweenPosition/TweenSize/TweenSizeAndPosition` | `TweenService:Create()` |
| `GuiObject.Draggable`, `DragBegin`, `DragStopped` | `UIDragDetector` |
| `GuiObject.BackgroundColor/BorderColor/Transparency` | `BackgroundColor3`/`BorderColor3`/`BackgroundTransparency` |
| `TextLabel/TextButton/TextBox.FontSize`, `TextColor`, `TextWrap` | `TextSize`, `TextColor3`, `TextWrapped` |
| `StarterGui.ResetPlayerGuiOnSpawn` | `ScreenGui.ResetOnSpawn` |
| `GuiService:IsTenFootInterface()` (superseded) | `GuiService.ViewportDisplaySize` |
| `GuiService.IsModalDialog`, `IsWindows`, `AddSelectionParent/Tuple`, `RemoveSelectionGroup` | `SelectionGroup`, `UserInputService.PreferredInput` |
| `UIGridStyleLayout:SetCustomSortFunction` | `SortOrder = LayoutOrder`/`Name` |
| `Mouse.KeyDown/KeyUp` | `UserInputService` / Input Action System |
| `UserInputService.ModalEnabled` | `GuiService.TouchControlsEnabled` |
| `UserInputService.VREnabled`, `UserHeadCFrame`, `GetUserCFrame`, `UserCFrameChanged` | `VRService` equivalents |
| `ContextActionService:BindActionToInputTypes` | `BindAction` (or Input Action System) |
| `InputAction:Fire()` | `InputBinding:Fire()` |
| `UserGameSettings.ControlMode` | `UserInputService.MouseBehavior` for shift-lock style control |

## Services

| Deprecated | Use |
| --- | --- |
| `MarketplaceService:GetProductInfo()` | `GetProductInfoAsync()` |
| `MarketplaceService:PlayerOwnsAsset()` / `PlayerOwnsBundle()` | `...Async()` variants |
| `MarketplaceService:PromptPremiumPurchase()` | `PromptRobloxSubscriptionPurchase()` |
| `GamePassService:PlayerHasPass()` | `MarketplaceService:UserOwnsGamePassAsync()` |
| `BadgeService:AwardBadge()` / `UserHasBadge()` / `IsDisabled()` / `IsLegal()` | `AwardBadgeAsync()` / `UserHasBadgeAsync()` / `GetBadgeInfoAsync().IsEnabled` / — |
| `TeleportService:Teleport`, `TeleportToPlaceInstance`, `TeleportToPrivateServer`, `TeleportPartyAsync`, `TeleportToSpawnByName` | `TeleportService:TeleportAsync()` + `TeleportOptions` |
| `TeleportService:ReserveServer()` | `ReserveServerAsync()` |
| `TeleportService.CustomizedTeleportUI` | `SetTeleportGui` |
| `GlobalDataStore:OnUpdate()` | `MessagingService` |
| `DataStore:RemoveVersionAsync()` | versions expire automatically; `RemoveAsync` for keys |
| `PathfindingService:FindPathAsync()` (superseded), `ComputeRawPathAsync`, `ComputeSmoothPathAsync`, `Path:GetPointCoordinates`, `Path:CheckOcclusionAsync` | `CreatePath()` + `Path:ComputeAsync()`, `GetWaypoints()`, `Path.Blocked` |
| `AnalyticsService:FireEvent/FireCustomEvent/FireInGameEconomyEvent/FirePlayerProgressionEvent/FireLogEvent` | `LogCustomEvent`, `LogEconomyEvent`, `LogProgressionEvent` (+ Start/Complete/Fail), `LogFunnelStepEvent` |
| `Chat` service, `Chat:FilterStringForPlayerAsync`, legacy ChatService modules, `TextChatService.ChatVersion` | `TextChatService`; `TextService:FilterStringAsync` |
| `TextFilterResult:GetChatForUserAsync()` (returns empty string) | `TextChannel`s for chat; `GetNonChatStringForUserAsync/ForBroadcastAsync` for other text |
| `TextService:FilterAndTranslateStringAsync()` | `FilterStringAsync` |
| `LocalizationService:GetTranslatorForPlayer()` | `GetTranslatorForPlayerAsync()` |
| `LocalizationTable:GetString/GetContents/SetContents/SetEntry/RemoveKey`, `DevelopmentLanguage` | `GetTranslator`, `GetEntries/SetEntries`, `RemoveEntry`, `SourceLocaleId` |
| `InsertService:Insert/GetFreeModels/GetFreeDecals`, sets APIs | `LoadAsset`, `GetFreeModelsAsync`, `GetFreeDecalsAsync` |
| `AssetService:SearchAudio/GetAssetIdsForPackage` | `SearchAudioAsync`/`GetAssetIdsForPackageAsync` |
| `AudioPlayer.AssetId` | `AudioPlayer.Asset` |
| `Sound.Pitch`, `Sound.MinDistance/MaxDistance/EmitterSize` | `PlaybackSpeed`, `RollOffMinDistance/RollOffMaxDistance` |
| `SocialService:PromptLinkSharing()` | `PromptLinkSharingAsync()` |
| `OpenCloudService`, `OpenCloudApiV1` | `HttpService:RequestAsync` with an API key secret |
| `ContentProvider:Preload()` | `PreloadAsync()` |
| `Stats.HeartbeatTimeMs/PhysicsStepTimeMs` | `HeartbeatTime`/`PhysicsStepTime` |
| `TestService:Run()`, `FunctionalTest` | `TestService:RunAsync()` / a test framework (Jest Lua) |
| `Teams:RebalanceTeams()`, `Team.Score`, `Team.AutoColorCharacters` | custom logic |
| `PointsService` | badges / your own progression |
| `AdService:ShowVideoAd`, `AdGui.OnAdEvent` | Rewarded video via `AdService:ShowRewardedVideoAdAsync` |
| `GenerationService:GenerateMeshAsync` (scheduled for deprecation) | `GenerateModelAsync` |
