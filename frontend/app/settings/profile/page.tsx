'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
    ChangeEvent,
    FormEvent,
    PointerEvent as ReactPointerEvent,
    useEffect,
    useRef,
    useState,
} from 'react';

import {
    ArrowLeft,
    Camera,
    Check,
    ImagePlus,
    Loader2,
    Save,
    Trash2,
    X,
} from 'lucide-react';

import FadeIn from '@/components/FadeIn';
import HomeNav from '@/components/special/HomeNav';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { ApiError, apiRequest, getMediaUrl } from '@/lib/api';

type UserProfile = {
    id: string | number;
    username: string;
    display_name: string;
    bio: string;
    profile_image: string | null;
};

type CurrentUserResponse = {
    user: UserProfile;
};

type ProfileUpdateResponse = {
    message: string;
    user: UserProfile;
};

type ProfileErrors = {
    username?: string;
    display_name?: string;
    bio?: string;
    profile_image?: string;
};

type CropBox = {
    x: number;
    y: number;
    size: number;
};

type CropInteraction = {
    pointerId: number;
    handle: string;
    startX: number;
    startY: number;
    initialCrop: CropBox;
};

type ImageViewerDirection =
    | 'left'
    | 'right'
    | 'up'
    | 'down'
    | null;

type ImageViewerPointer = {
    pointerId: number;
    startX: number;
    startY: number;
};

const BIO_MAX_LENGTH = 160;
const PROFILE_IMAGE_SIZE = 512;
const PROFILE_IMAGE_QUALITY = 0.92;
const MIN_CROP_SIZE = 0.15;

const USERNAME_PATTERN = /^[A-Za-z0-9_]{3,30}$/;

function getGraphemes(value: string): string[] {
    const IntlWithSegmenter = Intl as typeof Intl & {
        Segmenter?: new (
            locale?: string,
            options?: { granularity: 'grapheme' },
        ) => {
            segment: (input: string) => Iterable<{
                segment: string;
            }>;
        };
    };

    if (typeof IntlWithSegmenter.Segmenter === 'function') {
        const segmenter = new IntlWithSegmenter.Segmenter(
            undefined,
            { granularity: 'grapheme' },
        );

        return Array.from(
            segmenter.segment(value),
            (item) => item.segment,
        );
    }

    return Array.from(value);
}

function countCharacters(value: string): number {
    return getGraphemes(value).length;
}

function getInitials(
    displayName: string,
    username: string,
): string {
    const value = displayName.trim() || username.trim();

    if (!value) {
        return 'V';
    }

    const words = value.split(/\s+/);

    if (words.length > 1) {
        return (
            words[0].charAt(0) +
            words[1].charAt(0)
        ).toUpperCase();
    }

    return value.slice(0, 2).toUpperCase();
}

function getApiFieldError(
    error: ApiError,
    field: string,
): string | undefined {
    const value = error.data?.[field];

    if (typeof value === 'string') {
        return value;
    }

    if (Array.isArray(value) && value.length > 0) {
        return String(value[0]);
    }

    return undefined;
}

function clamp(
    value: number,
    minimum: number,
    maximum: number,
): number {
    return Math.min(
        Math.max(value, minimum),
        maximum,
    );
}

function createInitialCrop(
    imageWidth: number,
    imageHeight: number,
): CropBox {
    const shorterSide = Math.min(
        imageWidth,
        imageHeight,
    );

    const size = 0.75;

    return {
        x: (
            imageWidth / shorterSide - size
        ) / 2,
        y: (
            imageHeight / shorterSide - size
        ) / 2,
        size,
    };
}

function getCropStyle(
    crop: CropBox,
    imageWidth: number,
    imageHeight: number,
): React.CSSProperties {
    const shorterSide = Math.min(
        imageWidth,
        imageHeight,
    );

    return {
        left: `${(crop.x * shorterSide / imageWidth) * 100}%`,
        top: `${(crop.y * shorterSide / imageHeight) * 100}%`,
        width: `${(crop.size * shorterSide / imageWidth) * 100}%`,
        height: `${(crop.size * shorterSide / imageHeight) * 100}%`,
    };
}

async function createCroppedImage(
    sourceUrl: string,
    crop: CropBox,
    imageWidth: number,
    imageHeight: number,
): Promise<File> {
    const image = new window.Image();

    image.src = sourceUrl;

    await new Promise<void>((resolve, reject) => {
        image.onload = () => resolve();
        image.onerror = () => reject(
            new Error('Unable to process this image.'),
        );
    });

    const shorterSide = Math.min(
        imageWidth,
        imageHeight,
    );

    const sourceX = crop.x * shorterSide;
    const sourceY = crop.y * shorterSide;
    const sourceSize = crop.size * shorterSide;

    const canvas = document.createElement('canvas');

    canvas.width = PROFILE_IMAGE_SIZE;
    canvas.height = PROFILE_IMAGE_SIZE;

    const context = canvas.getContext('2d');

    if (!context) {
        throw new Error(
            'Your browser could not prepare the cropped image.',
        );
    }

    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = 'high';

    context.drawImage(
        image,
        sourceX,
        sourceY,
        sourceSize,
        sourceSize,
        0,
        0,
        PROFILE_IMAGE_SIZE,
        PROFILE_IMAGE_SIZE,
    );

    const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(
            resolve,
            'image/webp',
            PROFILE_IMAGE_QUALITY,
        );
    });

    if (!blob) {
        throw new Error(
            'Unable to optimize the cropped image. Please try another image.',
        );
    }

    return new File(
        [blob],
        'profile-picture.webp',
        {
            type: 'image/webp',
            lastModified: Date.now(),
        },
    );
}

export default function ProfileSettingsPage() {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const cropStageRef = useRef<HTMLDivElement>(null);
    const cropInteractionRef = useRef<CropInteraction | null>(null);

    const imageViewerPointerRef =
        useRef<ImageViewerPointer | null>(null);

    const imageViewerCloseTimeoutRef =
        useRef<ReturnType<typeof setTimeout> | null>(null);

    const [isImageViewerOpen, setIsImageViewerOpen] =
        useState(false);

    const [isImageViewerClosing, setIsImageViewerClosing] =
        useState(false);

    const [imageViewerCloseDirection, setImageViewerCloseDirection] =
        useState<ImageViewerDirection>(null);

    const [profile, setProfile] =
        useState<UserProfile | null>(null);

    const [username, setUsername] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [bio, setBio] = useState('');

    const [selectedImage, setSelectedImage] =
        useState<File | null>(null);

    const [removeImage, setRemoveImage] = useState(false);

    const [imagePreview, setImagePreview] =
        useState<string | null>(null);

    const [cropSource, setCropSource] = useState<{
        file: File;
        url: string;
    } | null>(null);

    const [cropImageDimensions, setCropImageDimensions] =
        useState({
            width: 0,
            height: 0,
        });

    const [crop, setCrop] = useState<CropBox | null>(null);
    const [isCropping, setIsCropping] = useState(false);
    const [cropError, setCropError] = useState('');

    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    const [loadError, setLoadError] = useState('');
    const [saveError, setSaveError] = useState('');
    const [successMessage, setSuccessMessage] =
        useState('');

    const [fieldErrors, setFieldErrors] =
        useState<ProfileErrors>({});

    // ========================================================
    // Profile picture viewer
    // ========================================================

    const openImageViewer = () => {
        if (!visibleImage) {
            return;
        }

        setImageViewerCloseDirection(null);
        setIsImageViewerClosing(false);
        setIsImageViewerOpen(true);
    };

    const closeImageViewer = (
        direction: ImageViewerDirection = null,
    ) => {
        if (!isImageViewerOpen || isImageViewerClosing) {
            return;
        }

        setImageViewerCloseDirection(direction);
        setIsImageViewerClosing(true);

        imageViewerCloseTimeoutRef.current =
            setTimeout(() => {
                setIsImageViewerOpen(false);
                setIsImageViewerClosing(false);
                setImageViewerCloseDirection(null);
                imageViewerPointerRef.current = null;
                imageViewerCloseTimeoutRef.current = null;
            }, 300);
    };

    const handleImageViewerPointerDown = (
        event: ReactPointerEvent<HTMLDivElement>,
    ) => {
        if (isImageViewerClosing) {
            return;
        }

        event.preventDefault();

        imageViewerPointerRef.current = {
            pointerId: event.pointerId,
            startX: event.clientX,
            startY: event.clientY,
        };

        event.currentTarget.setPointerCapture(event.pointerId);
    };

    const handleImageViewerPointerUp = (
        event: ReactPointerEvent<HTMLDivElement>,
    ) => {
        const pointer = imageViewerPointerRef.current;

        if (
            !pointer ||
            pointer.pointerId !== event.pointerId
        ) {
            return;
        }

        const deltaX = event.clientX - pointer.startX;
        const deltaY = event.clientY - pointer.startY;

        imageViewerPointerRef.current = null;

        const threshold = 60;

        if (
            Math.abs(deltaX) < threshold &&
            Math.abs(deltaY) < threshold
        ) {
            return;
        }

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            closeImageViewer(
                deltaX > 0 ? 'right' : 'left',
            );
        } else {
            closeImageViewer(
                deltaY > 0 ? 'down' : 'up',
            );
        }
    };

    // ========================================================
    // Page title
    // ========================================================

    useEffect(() => {
        const previousTitle = document.title;

        document.title = 'Edit profile | VibeNationHQ';

        return () => {
            document.title = previousTitle;
        };
    }, []);

    // ========================================================
    // Image viewer keyboard and scroll handling
    // ========================================================

    useEffect(() => {
        if (!isImageViewerOpen) {
            return;
        }

        const previousOverflow = document.body.style.overflow;

        document.body.style.overflow = 'hidden';

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                closeImageViewer();
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            document.body.style.overflow = previousOverflow;

            window.removeEventListener(
                'keydown',
                handleKeyDown,
            );
        };
    }, [isImageViewerOpen, isImageViewerClosing]);

    useEffect(() => {
        return () => {
            if (imageViewerCloseTimeoutRef.current) {
                clearTimeout(imageViewerCloseTimeoutRef.current);
            }
        };
    }, []);

    // ========================================================
    // Load current profile
    // ========================================================

    useEffect(() => {
        let isMounted = true;

        const loadProfile = async () => {
            try {
                const data =
                    await apiRequest<CurrentUserResponse>(
                        '/api/accounts/me/',
                    );

                if (!isMounted) {
                    return;
                }

                setProfile(data.user);
                setUsername(data.user.username);
                setDisplayName(data.user.display_name);
                setBio(data.user.bio ?? '');
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                if (error instanceof ApiError) {
                    setLoadError(
                        error.data?.detail ??
                        'Unable to load your profile right now.',
                    );
                } else {
                    setLoadError(
                        'Unable to load your profile right now.',
                    );
                }
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        };

        loadProfile();

        return () => {
            isMounted = false;
        };
    }, []);

    // ========================================================
    // Selected image preview URL
    // ========================================================

    useEffect(() => {
        if (!selectedImage) {
            setImagePreview(null);
            return;
        }

        const objectUrl = URL.createObjectURL(
            selectedImage,
        );

        setImagePreview(objectUrl);

        return () => {
            URL.revokeObjectURL(objectUrl);
        };
    }, [selectedImage]);

    // ========================================================
    // Crop source URL cleanup
    // ========================================================

    useEffect(() => {
        return () => {
            if (cropSource?.url) {
                URL.revokeObjectURL(cropSource.url);
            }
        };
    }, [cropSource]);

    // ========================================================
    // Derived values
    // ========================================================

    const currentImageUrl =
        profile?.profile_image && !removeImage
            ? getMediaUrl(profile.profile_image)
            : null;

    const visibleImage =
        imagePreview || currentImageUrl;

    const initials = getInitials(
        displayName,
        username,
    );

    const bioCharacterCount = countCharacters(bio);

    const hasChanges =
        !!profile &&
        (
            username !== profile.username ||
            displayName !== profile.display_name ||
            bio !== (profile.bio ?? '') ||
            selectedImage !== null ||
            removeImage
        );

    const cropStageAspectRatio =
        cropImageDimensions.width > 0 &&
            cropImageDimensions.height > 0
            ? cropImageDimensions.width /
            cropImageDimensions.height
            : 1;

    // ========================================================
    // Shared input feedback
    // ========================================================

    const clearSaveFeedback = () => {
        setSaveError('');
        setSuccessMessage('');
    };

    // ========================================================
    // Input handlers
    // ========================================================

    const handleUsernameChange = (
        event: ChangeEvent<HTMLInputElement>,
    ) => {
        const value = event.target.value.replace(/\s/g, '');

        setUsername(value);

        setFieldErrors((previous) => ({
            ...previous,
            username: undefined,
        }));

        clearSaveFeedback();
    };

    const handleDisplayNameChange = (
        event: ChangeEvent<HTMLInputElement>,
    ) => {
        setDisplayName(event.target.value);

        setFieldErrors((previous) => ({
            ...previous,
            display_name: undefined,
        }));

        clearSaveFeedback();
    };

    const handleBioChange = (
        event: ChangeEvent<HTMLTextAreaElement>,
    ) => {
        const characters = getGraphemes(
            event.target.value,
        );

        setBio(
            characters
                .slice(0, BIO_MAX_LENGTH)
                .join(''),
        );

        setFieldErrors((previous) => ({
            ...previous,
            bio: undefined,
        }));

        clearSaveFeedback();
    };

    // ========================================================
    // Open and close cropper
    // ========================================================

    const closeCropper = () => {
        setCropSource(null);
        setCrop(null);
        setCropImageDimensions({
            width: 0,
            height: 0,
        });
        setCropError('');
        setIsCropping(false);
        cropInteractionRef.current = null;

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleImageSelection = (
        event: ChangeEvent<HTMLInputElement>,
    ) => {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith('image/')) {
            setFieldErrors((previous) => ({
                ...previous,
                profile_image: 'Please select a valid image file.',
            }));

            event.target.value = '';
            return;
        }

        if (file.size > 20 * 1024 * 1024) {
            setFieldErrors((previous) => ({
                ...previous,
                profile_image:
                    'Please choose an image smaller than 20 MB.',
            }));

            event.target.value = '';
            return;
        }

        const url = URL.createObjectURL(file);

        setCropSource({
            file,
            url,
        });

        setCrop(null);
        setCropError('');

        setFieldErrors((previous) => ({
            ...previous,
            profile_image: undefined,
        }));

        clearSaveFeedback();
    };

    const handleCropImageLoad = (
        event: React.SyntheticEvent<HTMLImageElement>,
    ) => {
        const image = event.currentTarget;

        const width = image.naturalWidth;
        const height = image.naturalHeight;

        setCropImageDimensions({
            width,
            height,
        });

        setCrop(
            createInitialCrop(width, height),
        );
    };

    // ========================================================
    // Crop interaction
    // ========================================================

    const handleCropPointerDown = (
        event: ReactPointerEvent<HTMLDivElement>,
    ) => {
        if (!crop || !cropImageDimensions.width) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const handle =
            event.currentTarget.dataset.handle ?? 'move';

        cropInteractionRef.current = {
            pointerId: event.pointerId,
            handle,
            startX: event.clientX,
            startY: event.clientY,
            initialCrop: crop,
        };

        event.currentTarget.setPointerCapture(
            event.pointerId,
        );
    };

    const handleCropPointerMove = (
        event: ReactPointerEvent<HTMLDivElement>,
    ) => {
        const interaction = cropInteractionRef.current;

        if (
            !interaction ||
            interaction.pointerId !== event.pointerId ||
            !cropImageDimensions.width ||
            !cropImageDimensions.height
        ) {
            return;
        }

        const stage = cropStageRef.current;

        if (!stage) {
            return;
        }

        const bounds = stage.getBoundingClientRect();

        const shorterSide = Math.min(
            cropImageDimensions.width,
            cropImageDimensions.height,
        );

        const scale = bounds.width /
            cropImageDimensions.width;

        const deltaX =
            (event.clientX - interaction.startX) /
            scale /
            shorterSide;

        const deltaY =
            (event.clientY - interaction.startY) /
            scale /
            shorterSide;

        const initial = interaction.initialCrop;
        const handle = interaction.handle;

        const maxX =
            cropImageDimensions.width / shorterSide -
            initial.size;

        const maxY =
            cropImageDimensions.height / shorterSide -
            initial.size;

        if (handle === 'move') {
            setCrop({
                ...initial,
                x: clamp(
                    initial.x + deltaX,
                    0,
                    maxX,
                ),
                y: clamp(
                    initial.y + deltaY,
                    0,
                    maxY,
                ),
            });

            return;
        }

        const horizontalDirection =
            handle.includes('left')
                ? -1
                : handle.includes('right')
                    ? 1
                    : 0;

        const verticalDirection =
            handle.includes('top')
                ? -1
                : handle.includes('bottom')
                    ? 1
                    : 0;

        let sizeChange = 0;

        if (
            horizontalDirection !== 0 &&
            verticalDirection !== 0
        ) {
            const horizontalChange =
                deltaX * horizontalDirection;

            const verticalChange =
                deltaY * verticalDirection;

            sizeChange =
                Math.abs(horizontalChange) >
                    Math.abs(verticalChange)
                    ? horizontalChange
                    : verticalChange;
        } else if (horizontalDirection !== 0) {
            sizeChange =
                deltaX * horizontalDirection;
        } else {
            sizeChange =
                deltaY * verticalDirection;
        }

        const imageWidthInUnits =
            cropImageDimensions.width / shorterSide;

        const imageHeightInUnits =
            cropImageDimensions.height / shorterSide;

        const maximumHorizontalSize =
            horizontalDirection === -1
                ? initial.x + initial.size
                : horizontalDirection === 1
                    ? imageWidthInUnits - initial.x
                    : imageWidthInUnits;

        const maximumVerticalSize =
            verticalDirection === -1
                ? initial.y + initial.size
                : verticalDirection === 1
                    ? imageHeightInUnits - initial.y
                    : imageHeightInUnits;

        const maximumSize = Math.min(
            maximumHorizontalSize,
            maximumVerticalSize,
        );

        const nextSize = clamp(
            initial.size + sizeChange,
            MIN_CROP_SIZE,
            maximumSize,
        );

        let nextX = initial.x;
        let nextY = initial.y;

        if (horizontalDirection === -1) {
            nextX = initial.x +
                initial.size -
                nextSize;
        }

        if (verticalDirection === -1) {
            nextY = initial.y +
                initial.size -
                nextSize;
        }

        setCrop({
            x: clamp(
                nextX,
                0,
                cropImageDimensions.width / shorterSide -
                nextSize,
            ),
            y: clamp(
                nextY,
                0,
                cropImageDimensions.height / shorterSide -
                nextSize,
            ),
            size: nextSize,
        });
    };

    const handleCropPointerUp = (
        event: ReactPointerEvent<HTMLDivElement>,
    ) => {
        const interaction = cropInteractionRef.current;

        if (
            interaction?.pointerId === event.pointerId
        ) {
            cropInteractionRef.current = null;
        }
    };

    const handleCropReset = () => {
        if (
            !cropImageDimensions.width ||
            !cropImageDimensions.height
        ) {
            return;
        }

        setCrop(
            createInitialCrop(
                cropImageDimensions.width,
                cropImageDimensions.height,
            ),
        );
    };

    // ========================================================
    // Confirm crop and optimize image
    // ========================================================

    const handleConfirmCrop = async () => {
        if (
            !cropSource ||
            !crop ||
            !cropImageDimensions.width ||
            !cropImageDimensions.height
        ) {
            return;
        }

        setIsCropping(true);
        setCropError('');

        try {
            const optimizedImage = await createCroppedImage(
                cropSource.url,
                crop,
                cropImageDimensions.width,
                cropImageDimensions.height,
            );

            setSelectedImage(optimizedImage);
            setRemoveImage(false);

            setFieldErrors((previous) => ({
                ...previous,
                profile_image: undefined,
            }));

            closeCropper();
            clearSaveFeedback();
        } catch (error) {
            setCropError(
                error instanceof Error
                    ? error.message
                    : 'Unable to crop this image. Please try again.',
            );
        } finally {
            setIsCropping(false);
        }
    };

    // ========================================================
    // Remove and undo image changes
    // ========================================================

    const handleRemoveImage = () => {
        setSelectedImage(null);
        setRemoveImage(true);

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }

        setFieldErrors((previous) => ({
            ...previous,
            profile_image: undefined,
        }));

        clearSaveFeedback();
    };

    const handleCancelImageChange = () => {
        setSelectedImage(null);
        setRemoveImage(false);

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }

        setFieldErrors((previous) => ({
            ...previous,
            profile_image: undefined,
        }));

        clearSaveFeedback();
    };

    // ========================================================
    // Client-side validation
    // ========================================================

    const validateForm = (): boolean => {
        const errors: ProfileErrors = {};

        const trimmedUsername = username.trim();
        const trimmedDisplayName = displayName.trim();

        if (!trimmedUsername) {
            errors.username = 'Username is required.';
        } else if (
            !USERNAME_PATTERN.test(trimmedUsername)
        ) {
            errors.username =
                'Use 3–30 characters: letters, numbers, and underscores only.';
        }

        if (!trimmedDisplayName) {
            errors.display_name =
                'Display name cannot be empty.';
        } else if (trimmedDisplayName.length > 100) {
            errors.display_name =
                'Display name cannot exceed 100 characters.';
        }

        if (bioCharacterCount > BIO_MAX_LENGTH) {
            errors.bio =
                `Bio cannot exceed ${BIO_MAX_LENGTH} characters.`;
        }

        setFieldErrors(errors);

        return Object.keys(errors).length === 0;
    };

    // ========================================================
    // Save profile
    // ========================================================

    const handleSubmit = async (
        event: FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        if (!profile || isSaving) {
            return;
        }

        setSaveError('');
        setSuccessMessage('');
        setFieldErrors({});

        if (!validateForm()) {
            return;
        }

        setIsSaving(true);

        try {
            let data: ProfileUpdateResponse;

            const payload = {
                username: username.trim(),
                display_name: displayName.trim(),
                bio,
            };

            if (selectedImage) {
                const formData = new FormData();

                formData.append(
                    'username',
                    payload.username,
                );

                formData.append(
                    'display_name',
                    payload.display_name,
                );

                formData.append(
                    'bio',
                    payload.bio,
                );

                formData.append(
                    'profile_image',
                    selectedImage,
                );

                data =
                    await apiRequest<ProfileUpdateResponse>(
                        '/api/accounts/profile/',
                        {
                            method: 'PATCH',
                            body: formData,
                        },
                    );
            } else {
                const jsonPayload = {
                    ...payload,
                    ...(removeImage
                        ? { profile_image: null }
                        : {}),
                };

                data =
                    await apiRequest<ProfileUpdateResponse>(
                        '/api/accounts/profile/',
                        {
                            method: 'PATCH',
                            body: JSON.stringify(jsonPayload),
                        },
                    );
            }

            setProfile(data.user);
            setUsername(data.user.username);
            setDisplayName(data.user.display_name);
            setBio(data.user.bio ?? '');

            setSelectedImage(null);
            setRemoveImage(false);

            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }

            setSuccessMessage(
                data.message ||
                'Your profile has been updated successfully.',
            );
        } catch (error) {
            if (error instanceof ApiError) {
                const errors: ProfileErrors = {
                    username: getApiFieldError(
                        error,
                        'username',
                    ),
                    display_name: getApiFieldError(
                        error,
                        'display_name',
                    ),
                    bio: getApiFieldError(
                        error,
                        'bio',
                    ),
                    profile_image: getApiFieldError(
                        error,
                        'profile_image',
                    ),
                };

                setFieldErrors(errors);

                const hasFieldErrors = Object.values(
                    errors,
                ).some(Boolean);

                if (!hasFieldErrors) {
                    setSaveError(
                        error.data?.detail ??
                        error.message ??
                        'Unable to update your profile. Please try again.',
                    );
                }
            } else {
                setSaveError(
                    'Unable to update your profile. Please try again.',
                );
            }
        } finally {
            setIsSaving(false);
        }
    };

    // ========================================================
    // Loading state and page
    // ========================================================

    return (
        <ProtectedRoute>
            <div
                className="
                min-h-screen
                bg-light-bg
                text-light-text
                transition-colors duration-300
                dark:bg-dark-bg
                dark:text-dark-text
                "
            >
                <HomeNav />

                <main
                    className="
                        mx-auto w-full max-w-4xl
                        px-4 py-8
                        sm:px-6 sm:py-10
                        lg:px-8 lg:py-12
                    "
                >
                    <FadeIn>
                        <div className="py-3 sm:py-5">
                            <button
                            type="button"
                            onClick={() => window.history.back()}
                            className="inline-flex items-center gap-2 rounded-lg text-xs font-medium text-light-muted transition-colors hover:text-brand-teal dark:text-dark-muted dark:hover:text-brand-teal sm:text-sm"
                            >
                            <ArrowLeft className="h-4 w-4" />
                            Back
                            </button>
                        </div>

                        <div className="mt-7">
                            <p
                                className="
                                text-sm font-semibold
                                text-brand-teal-dark
                                dark:text-brand-teal-light
                                "
                            >
                                Personal information
                            </p>

                            <h1
                                className="
                                    mt-2 text-3xl font-black tracking-tight
                                    text-light-text
                                    dark:text-dark-text
                                    sm:text-4xl
                                    "
                            >
                                Edit profile
                            </h1>

                            <p
                                className="
                                mt-3 max-w-2xl text-sm leading-6
                                text-light-text-muted
                                dark:text-dark-text-muted
                                sm:text-base
                                "
                            >
                                Manage how people see you across
                                VibeNationHQ. Your changes will also
                                appear on your public profile.
                            </p>
                        </div>
                    </FadeIn>

                    {isLoading ? (
                        <FadeIn className="mt-8">
                            <div
                                className="
                                    rounded-2xl
                                    border border-light-border
                                    bg-light-surface
                                    p-6
                                    dark:border-dark-border
                                    dark:bg-dark-surface
                                    sm:p-8
                                    "
                            >
                                <div className="animate-pulse">
                                    <div className="flex items-center gap-4">
                                        <div
                                            className="
                                                h-20 w-20 rounded-full
                                                bg-light-surface-muted
                                                dark:bg-dark-surface-muted
                                            "
                                        />

                                        <div className="flex-1">
                                            <div
                                                className="
                                                    h-4 w-32 rounded
                                                    bg-light-surface-muted
                                                    dark:bg-dark-surface-muted
                                                    "
                                            />

                                            <div
                                                className="
                                                    mt-3 h-3 w-48 rounded
                                                    bg-light-surface-muted
                                                    dark:bg-dark-surface-muted
                                                    "
                                            />
                                        </div>
                                    </div>

                                    <div className="mt-9 space-y-6">
                                        <div
                                            className="
                                                h-12 rounded-xl
                                                bg-light-surface-soft
                                                dark:bg-dark-surface-soft
                                            "
                                        />

                                        <div
                                            className="
                                                h-12 rounded-xl
                                                bg-light-surface-soft
                                                dark:bg-dark-surface-soft
                                            "
                                        />

                                        <div
                                            className="
                                                h-28 rounded-xl
                                                bg-light-surface-soft
                                                dark:bg-dark-surface-soft
                                            "
                                        />
                                    </div>
                                </div>
                            </div>
                        </FadeIn>
                    ) : loadError ? (
                        <FadeIn className="mt-8">
                            <div
                                role="alert"
                                className="
                                    rounded-xl
                                    border border-red-200
                                    bg-red-50
                                    px-4 py-4
                                    text-sm leading-6
                                    text-red-700
                                    dark:border-red-500/20
                                    dark:bg-red-500/10
                                    dark:text-red-300
                                    "
                            >
                                {loadError}
                            </div>
                        </FadeIn>
                    ) : profile ? (
                        <FadeIn className="mt-8">
                            <form
                                onSubmit={handleSubmit}
                                className="
                                    overflow-hidden
                                    rounded-2xl
                                    border border-light-border
                                    bg-light-surface
                                    shadow-sm shadow-black/[0.03]
                                    dark:border-dark-border
                                    dark:bg-dark-surface
                                    dark:shadow-black/10
                                    "
                            >
                                {/* Profile picture */}
                                <section
                                    className="
                                    border-b border-light-border-soft
                                    px-5 py-7
                                    dark:border-dark-border-soft
                                    sm:px-7
                                "
                                >
                                    <h2
                                        className="
                                        text-base font-bold
                                        text-light-text
                                        dark:text-dark-text
                                        "
                                    >
                                        Profile picture
                                    </h2>

                                    <p
                                        className="
                                            mt-1 text-sm
                                            text-light-text-muted
                                            dark:text-dark-text-muted
                                            "
                                    >
                                        Choose a picture that represents you.
                                    </p>

                                    <div className="
                                        mt-6 flex flex-col gap-5
                                        sm:flex-row sm:items-center
                                        ">
                                        <div className="flex shrink-0 items-center gap-4">
                                            <div
                                                className="
                                                    relative flex h-24 w-24 shrink-0
                                                    items-center justify-center
                                                    rounded-full
                                                    border border-light-border
                                                    bg-brand-teal/10
                                                    text-2xl font-black
                                                    text-brand-teal-dark
                                                    dark:border-dark-border
                                                    dark:bg-brand-teal/15
                                                    dark:text-brand-teal-light
                                                    "
                                            >
                                                <div className="
                                                    relative h-full w-full
                                                    overflow-hidden rounded-full
                                                    ">
                                                    {visibleImage ? (
                                                        <>
                                                            <Image
                                                                src={visibleImage}
                                                                alt="Profile picture preview"
                                                                fill
                                                                sizes="96px"
                                                                className="pointer-events-none object-cover"
                                                            />

                                                            <button
                                                                type="button"
                                                                onClick={openImageViewer}
                                                                aria-label="View profile picture"
                                                                title="View profile picture"
                                                                className="
                                                                    absolute inset-0 z-[1]
                                                                    cursor-pointer rounded-full
                                                                    focus:outline-none
                                                                    focus:ring-4
                                                                    focus:ring-brand-teal/30
                                                                "
                                                            />
                                                        </>
                                                    ) : (
                                                        <div className="
                                                            flex h-full w-full
                                                            items-center justify-center
                                                            ">
                                                            {initials}
                                                        </div>
                                                    )}
                                                </div>

                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        fileInputRef.current?.click()
                                                    }
                                                    aria-label={
                                                        selectedImage
                                                            ? 'Choose another profile picture'
                                                            : 'Upload profile picture'
                                                    }
                                                    title="Upload profile picture"
                                                    className="
                                                        absolute -bottom-0.5 -right-0.5
                                                        z-10 flex h-9 w-9
                                                        items-center justify-center
                                                        rounded-full
                                                        border-[3px] border-light-surface
                                                        bg-brand-teal
                                                        text-white
                                                        shadow-md
                                                        transition-all
                                                        hover:scale-105
                                                        hover:bg-brand-teal-dark
                                                        focus:outline-none
                                                        focus:ring-4
                                                        focus:ring-brand-teal/25
                                                        dark:border-dark-surface
                                                    "
                                                >
                                                    {selectedImage ? (
                                                        <ImagePlus className="h-4 w-4" />
                                                    ) : (
                                                        <Camera className="h-4 w-4" />
                                                    )}
                                                </button>
                                            </div>

                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept="image/*"
                                                onChange={handleImageSelection}
                                                className="hidden"
                                            />

                                            <div className="min-w-0 sm:hidden">
                                                <p className="
                                                    text-sm font-semibold
                                                    text-light-text
                                                    dark:text-dark-text
                                                    ">
                                                    Change picture
                                                </p>

                                                <p className="
                                                    mt-1 text-xs leading-5
                                                    text-light-text-muted
                                                    dark:text-dark-text-muted
                                                    ">
                                                    Tap the camera icon to upload.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="min-w-0 flex-1">
                                            <p className="
                                                hidden text-sm font-semibold
                                                text-light-text
                                                dark:text-dark-text
                                                sm:block
                                            ">
                                                Update your picture
                                            </p>

                                            <p className="
                                                mt-1 text-xs leading-5
                                                text-light-text-muted
                                                dark:text-dark-text-muted
                                            ">
                                                Select a picture using the camera button.
                                                You can adjust its framing before saving.
                                            </p>

                                            <div className="mt-3 flex flex-wrap items-center gap-3">
                                                {(selectedImage || removeImage) && (
                                                    <button
                                                        type="button"
                                                        onClick={handleCancelImageChange}
                                                        className="
                                                            inline-flex items-center
                                                            justify-center gap-2
                                                            rounded-lg
                                                            border border-light-border
                                                            px-3 py-2
                                                            text-xs font-semibold
                                                            text-light-text-muted
                                                            transition-colors
                                                            hover:bg-light-surface-soft
                                                            dark:border-dark-border
                                                            dark:text-dark-text-muted
                                                            dark:hover:bg-dark-surface-soft
                                                            "
                                                    >
                                                        <X className="h-3.5 w-3.5" />
                                                        Undo change
                                                    </button>
                                                )}

                                                {!selectedImage &&
                                                    !removeImage &&
                                                    profile.profile_image && (
                                                        <button
                                                            type="button"
                                                            onClick={handleRemoveImage}
                                                            className="
                                                                    inline-flex items-center
                                                                    justify-center gap-2
                                                                    rounded-lg
                                                                    border border-red-200
                                                                    px-3 py-2
                                                                    text-xs font-semibold
                                                                    text-red-600
                                                                    transition-colors
                                                                    hover:bg-red-50
                                                                    dark:border-red-500/20
                                                                    dark:text-red-400
                                                                    dark:hover:bg-red-500/10
                                                                "
                                                        >
                                                            <Trash2 className="h-3.5 w-3.5" />
                                                            Remove picture
                                                        </button>
                                                    )}
                                            </div>

                                            {selectedImage && (
                                                <p className="
                                                    mt-2 break-all text-xs font-medium
                                                    text-brand-teal-dark
                                                    dark:text-brand-teal-light
                                                    ">
                                                    Selected: {selectedImage.name}
                                                </p>
                                            )}

                                            {removeImage && (
                                                <p className="
                                                    mt-2 text-xs font-medium
                                                    text-red-600
                                                    dark:text-red-400
                                                    ">
                                                    Your picture will be removed when
                                                    you save your changes.
                                                </p>
                                            )}

                                            {fieldErrors.profile_image && (
                                                <p
                                                    className="
                                                        mt-2 text-xs
                                                        text-red-600
                                                        dark:text-red-400
                                                    "
                                                    role="alert"
                                                >
                                                    {fieldErrors.profile_image}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </section>

                                {/* Profile information */}
                                <section
                                    className="
                                        space-y-6
                                        px-5 py-7
                                        dark:border-dark-border-soft
                                        sm:px-7
                                    "
                                >
                                    <div>
                                        <h2
                                            className="
                                                text-base font-bold
                                                text-light-text
                                                dark:text-dark-text
                                            "
                                        >
                                            Profile information
                                        </h2>

                                        <p
                                            className="
                                                mt-1 text-sm
                                                text-light-text-muted
                                                dark:text-dark-text-muted
                                            "
                                        >
                                            These details appear on your public
                                            VibeNationHQ profile.
                                        </p>
                                    </div>

                                    {/* Display name */}
                                    <div>
                                        <label
                                            htmlFor="display-name"
                                            className="
                                                mb-2 block text-sm font-semibold
                                                text-light-text
                                                dark:text-dark-text
                                            "
                                        >
                                            Display name
                                        </label>

                                        <input
                                            id="display-name"
                                            type="text"
                                            value={displayName}
                                            onChange={handleDisplayNameChange}
                                            maxLength={100}
                                            autoComplete="name"
                                            placeholder="Your display name"
                                            className="
                                                w-full rounded-xl
                                                border border-light-border
                                                bg-light-bg
                                                px-4 py-3
                                                text-sm text-light-text
                                                outline-none
                                                transition-all
                                                placeholder:text-light-text-muted/70
                                                focus:border-brand-teal
                                                focus:ring-4
                                                focus:ring-brand-teal/10
                                                dark:border-dark-border
                                                dark:bg-dark-bg
                                                dark:text-dark-text
                                                dark:placeholder:text-dark-text-muted/70
                                            "
                                        />

                                        {fieldErrors.display_name && (
                                            <p
                                                className="mt-2 text-xs text-red-600 dark:text-red-400"
                                                role="alert"
                                            >
                                                {fieldErrors.display_name}
                                            </p>
                                        )}
                                    </div>

                                    {/* Username */}
                                    <div>
                                        <label
                                            htmlFor="username"
                                            className="
                                                mb-2 block text-sm font-semibold
                                                text-light-text
                                                dark:text-dark-text
                                            "
                                        >
                                            Username
                                        </label>

                                        <div
                                            className="
                                                flex items-center overflow-hidden
                                                rounded-xl
                                                border border-light-border
                                                bg-light-bg
                                                transition-all
                                                focus-within:border-brand-teal
                                                focus-within:ring-4
                                                focus-within:ring-brand-teal/10
                                                dark:border-dark-border
                                                dark:bg-dark-bg
                                            "
                                        >
                                            <span
                                                className="
                                                    select-none border-r
                                                    border-light-border
                                                    px-4 py-3
                                                    text-sm font-semibold
                                                    text-light-text-muted
                                                    dark:border-dark-border
                                                    dark:text-dark-text-muted
                                                    "
                                            >
                                                @
                                            </span>

                                            <input
                                                id="username"
                                                type="text"
                                                value={username}
                                                onChange={handleUsernameChange}
                                                minLength={3}
                                                maxLength={30}
                                                autoComplete="username"
                                                spellCheck={false}
                                                autoCapitalize="none"
                                                placeholder="username"
                                                className="
                                                    min-w-0 flex-1
                                                    bg-transparent
                                                    px-3 py-3 pr-4
                                                    text-sm text-light-text
                                                    outline-none
                                                    placeholder:text-light-text-muted/70
                                                    dark:text-dark-text
                                                    dark:placeholder:text-dark-text-muted/70
                                                    "
                                            />
                                        </div>

                                        <p
                                            className="
                                                mt-2 text-xs leading-5
                                                text-light-text-muted
                                                dark:text-dark-text-muted
                                            "
                                        >
                                            3–30 characters. Letters, numbers,
                                            and underscores only. Spaces are
                                            automatically removed.
                                        </p>

                                        {fieldErrors.username && (
                                            <p
                                                className="mt-2 text-xs text-red-600 dark:text-red-400"
                                                role="alert"
                                            >
                                                {fieldErrors.username}
                                            </p>
                                        )}
                                    </div>

                                    {/* Bio */}
                                    <div>
                                        <div className="mb-2 flex items-center justify-between gap-3">
                                            <label
                                                htmlFor="bio"
                                                className="
                                                    text-sm font-semibold
                                                    text-light-text
                                                    dark:text-dark-text
                                                    "
                                            >
                                                Bio
                                            </label>

                                            <span
                                                className={`
                                                    shrink-0 text-xs font-medium
                                                    ${bioCharacterCount >= BIO_MAX_LENGTH
                                                        ? 'text-amber-600 dark:text-amber-400'
                                                        : 'text-light-text-muted dark:text-dark-text-muted'
                                                    }
                                                    `}
                                            >
                                                {bioCharacterCount}/{BIO_MAX_LENGTH}
                                            </span>
                                        </div>

                                        <textarea
                                            id="bio"
                                            value={bio}
                                            onChange={handleBioChange}
                                            rows={4}
                                            placeholder="Tell people a little about yourself..."
                                            className="
                                                h-32 w-full resize-none
                                                overflow-y-auto rounded-xl
                                                border border-light-border
                                                bg-light-bg
                                                px-4 py-3
                                                text-sm leading-6
                                                text-light-text
                                                outline-none
                                                transition-all
                                                placeholder:text-light-text-muted/70
                                                focus:border-brand-teal
                                                focus:ring-4
                                                focus:ring-brand-teal/10
                                                dark:border-dark-border
                                                dark:bg-dark-bg
                                                dark:text-dark-text
                                                dark:placeholder:text-dark-text-muted/70
                                            "
                                        />

                                        <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
                                            <p
                                                className="
                                                    text-xs
                                                    text-light-text-muted
                                                    dark:text-dark-text-muted
                                                    "
                                            >
                                                Keep it short and let people know
                                                what you're about.
                                            </p>

                                            <p
                                                className="
                                                    text-xs
                                                    text-light-text-muted
                                                    dark:text-dark-text-muted
                                                    "
                                            >
                                                Emojis are welcome.
                                            </p>
                                        </div>

                                        {fieldErrors.bio && (
                                            <p
                                                className="mt-2 text-xs text-red-600 dark:text-red-400"
                                                role="alert"
                                            >
                                                {fieldErrors.bio}
                                            </p>
                                        )}
                                    </div>
                                </section>

                                {/* Save feedback */}
                                {(saveError || successMessage) && (
                                    <div className="px-5 sm:px-7">
                                        {saveError && (
                                            <div
                                                role="alert"
                                                className="
                                                    rounded-xl
                                                    border border-red-200
                                                    bg-red-50
                                                    px-4 py-3
                                                    text-sm leading-6
                                                    text-red-700
                                                    dark:border-red-500/20
                                                    dark:bg-red-500/10
                                                    dark:text-red-300
                                                    "
                                            >
                                                {saveError}
                                            </div>
                                        )}

                                        {successMessage && (
                                            <div
                                                role="status"
                                                className="
                                                    flex items-start gap-2
                                                    rounded-xl
                                                    border border-brand-teal/20
                                                    bg-brand-teal/5
                                                    px-4 py-3
                                                    text-sm leading-6
                                                    text-brand-teal-dark
                                                    dark:border-brand-teal/20
                                                    dark:bg-brand-teal/10
                                                    dark:text-brand-teal-light
                                                    "
                                            >
                                                <Check className="mt-0.5 h-4 w-4 shrink-0" />
                                                {successMessage}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Actions */}
                                <div
                                    className="
                                        flex flex-col-reverse gap-3
                                        border-t border-light-border-soft
                                        bg-light-surface-soft/60
                                        px-5 py-5
                                        dark:border-dark-border-soft
                                        dark:bg-dark-surface-soft/40
                                        sm:flex-row sm:items-center
                                        sm:justify-between
                                        sm:px-7
                                    "
                                >
                                    <p
                                        className="
                                            text-xs leading-5
                                            text-light-text-muted
                                            dark:text-dark-text-muted
                                            "
                                    >
                                        Your profile changes are visible
                                        wherever your profile appears.
                                    </p>

                                    <button
                                        type="submit"
                                        disabled={
                                            isSaving ||
                                            !hasChanges
                                        }
                                        className="
                                            inline-flex items-center
                                            justify-center gap-2
                                            rounded-xl
                                            bg-brand-teal
                                            px-5 py-3
                                            text-sm font-bold text-white
                                            transition-all
                                            hover:bg-brand-teal-dark
                                            focus:outline-none
                                            focus:ring-4
                                            focus:ring-brand-teal/20
                                            disabled:cursor-not-allowed
                                            disabled:opacity-50
                                            "
                                    >
                                        {isSaving ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Saving changes...
                                            </>
                                        ) : (
                                            <>
                                                <Save className="h-4 w-4" />
                                                Save changes
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </FadeIn>
                    ) : null}
                </main>

                {/* Profile picture lightbox */}
                {isImageViewerOpen && visibleImage && (
                    <div
                        role="dialog"
                        aria-modal="true"
                        aria-label="Profile picture viewer"
                        onClick={() => closeImageViewer()}
                        className={`
                            fixed inset-0 z-[110]
                            flex items-center justify-center
                            overflow-hidden
                            bg-black/35
                            p-4
                            backdrop-blur-xl
                            transition-opacity duration-300 ease-in-out
                            ${isImageViewerClosing
                                ? 'pointer-events-none opacity-0'
                                : 'opacity-100'
                            }
                        `}
                    >
                        {/* Image container */}
                        <div
                            onClick={(event) => event.stopPropagation()}
                            onPointerDown={handleImageViewerPointerDown}
                            onPointerUp={handleImageViewerPointerUp}
                            onPointerCancel={() => {
                                imageViewerPointerRef.current = null;
                            }}
                            className={`
                                relative
                                flex max-h-[78vh] max-w-[78vw]
                                items-center justify-center
                                touch-none select-none
                                transition-[transform,opacity]
                                duration-300 ease-in-out
                                ${isImageViewerClosing
                                    ? imageViewerCloseDirection === 'left'
                                        ? '-translate-x-[110vw] scale-95 opacity-0'
                                        : imageViewerCloseDirection === 'right'
                                            ? 'translate-x-[110vw] scale-95 opacity-0'
                                            : imageViewerCloseDirection === 'up'
                                                ? '-translate-y-[110vh] scale-95 opacity-0'
                                                : imageViewerCloseDirection === 'down'
                                                    ? 'translate-y-[110vh] scale-95 opacity-0'
                                                    : 'scale-90 opacity-0'
                                    : 'translate-x-0 translate-y-0 scale-100 opacity-100'
                                }
                            `}
                        >
                            <Image
                                src={visibleImage}
                                alt="Enlarged profile picture"
                                width={1200}
                                height={1200}
                                draggable={false}
                                className="
                                    max-h-[78vh]
                                    max-w-[78vw]
                                    rounded-2xl
                                    object-contain
                                    shadow-2xl shadow-black/30
                                "
                            />

                            {/* Close button positioned beside the image */}
                            <button
                                type="button"
                                onClick={(event) => {
                                    event.stopPropagation();
                                    closeImageViewer();
                                }}
                                aria-label="Close profile picture"
                                title="Close"
                                className="
                                    absolute -right-3 -top-3 z-20
                                    flex h-10 w-10
                                    items-center justify-center
                                    rounded-full
                                    border border-white/30
                                    bg-black/45
                                    text-white
                                    shadow-lg
                                    backdrop-blur-xl
                                    transition-all
                                    hover:rotate-90
                                    hover:bg-black/65
                                    focus:outline-none
                                    focus:ring-4
                                    focus:ring-white/25
                                    sm:-right-4 sm:-top-4
                                    sm:h-11 sm:w-11
                                "
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </div>

                        {/* Swipe guidance */}
                        <p
                            className="
                                pointer-events-none
                                absolute bottom-6 left-0 right-0
                                px-4
                                text-center text-xs font-medium
                                tracking-wide text-white/75
                            "
                        >
                            Swipe in any direction or tap outside to close
                        </p>
                    </div>
                )}

                {/* Image cropper */}
                {cropSource && (
                    <div
                        className="
                            fixed inset-0 z-[100]
                            flex items-center justify-center
                            overflow-y-auto
                            bg-black/70
                            p-4 backdrop-blur-sm
                        "
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="crop-dialog-title"
                    >
                        <div
                            className="
                                my-auto w-full max-w-2xl
                                overflow-hidden rounded-2xl
                                border border-light-border
                                bg-light-surface
                                shadow-2xl
                                dark:border-dark-border
                                dark:bg-dark-surface
                            "
                        >
                            <div
                                className="
                                    flex items-start justify-between gap-4
                                    border-b border-light-border-soft
                                    px-5 py-4
                                    dark:border-dark-border-soft
                                    sm:px-6
                                "
                            >
                                <div>
                                    <h2
                                        id="crop-dialog-title"
                                        className="
                                            text-lg font-bold
                                            text-light-text
                                            dark:text-dark-text
                                        "
                                    >
                                        Adjust profile picture
                                    </h2>

                                    <p
                                        className="
                                            mt-1 text-sm
                                            text-light-text-muted
                                            dark:text-dark-text-muted
                                        "
                                    >
                                        Move the square over the image and
                                        resize it to choose your framing.
                                    </p>
                                </div>

                                <button
                                    type="button"
                                    onClick={closeCropper}
                                    aria-label="Close image cropper"
                                    className="
                                        rounded-lg p-2
                                        text-light-text-muted
                                        transition-colors
                                        hover:bg-light-surface-soft
                                        hover:text-light-text
                                        dark:text-dark-text-muted
                                        dark:hover:bg-dark-surface-soft
                                        dark:hover:text-dark-text
                                    "
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="px-5 py-5 sm:px-6">
                                <div
                                    className="
                                        flex min-h-64 items-center justify-center
                                        overflow-hidden rounded-xl
                                        bg-black/90 p-3
                                    "
                                >
                                    <div
                                        ref={cropStageRef}
                                        className="
                                            relative mx-auto
                                            max-w-full overflow-hidden
                                            touch-none select-none
                                        "
                                        style={{
                                            width: `min(100%, 640px, ${55 * cropStageAspectRatio}vh)`,
                                            aspectRatio: `${cropStageAspectRatio}`,
                                        }}
                                    >
                                        <Image
                                            src={cropSource.url}
                                            alt="Image being cropped"
                                            fill
                                            sizes="(max-width: 640px) 100vw, 640px"
                                            draggable={false}
                                            onLoad={handleCropImageLoad}
                                            className="
                                                pointer-events-none
                                                select-none object-fill
                                            "
                                        />

                                        {crop && cropImageDimensions.width > 0 && (
                                            <>
                                                <div
                                                    className="
                                                        pointer-events-none absolute inset-0
                                                        bg-black/45
                                                    "
                                                />

                                                <div
                                                    data-handle="move"
                                                    onPointerDown={handleCropPointerDown}
                                                    onPointerMove={handleCropPointerMove}
                                                    onPointerUp={handleCropPointerUp}
                                                    onPointerCancel={handleCropPointerUp}
                                                    style={getCropStyle(
                                                        crop,
                                                        cropImageDimensions.width,
                                                        cropImageDimensions.height,
                                                    )}
                                                    className="
                                                        absolute z-10
                                                        cursor-move touch-none
                                                        border-2 border-white
                                                        shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]
                                                    "
                                                >
                                                    {[
                                                        'top-left',
                                                        'top-right',
                                                        'bottom-left',
                                                        'bottom-right',
                                                    ].map((handle) => (
                                                        <div
                                                            key={handle}
                                                            data-handle={handle}
                                                            onPointerDown={handleCropPointerDown}
                                                            onPointerMove={handleCropPointerMove}
                                                            onPointerUp={handleCropPointerUp}
                                                            onPointerCancel={handleCropPointerUp}
                                                            className={`
                                                                absolute z-20
                                                                h-4 w-4 rounded-sm
                                                                border-2 border-brand-teal
                                                                bg-white
                                                                ${handle.includes('top')
                                                                    ? '-top-2'
                                                                    : '-bottom-2'
                                                                }
                                                                ${handle.includes('left')
                                                                    ? '-left-2'
                                                                    : '-right-2'
                                                                }
                                                                ${handle.includes('top') &&
                                                                    handle.includes('left')
                                                                    ? 'cursor-nwse-resize'
                                                                    : handle.includes('top') &&
                                                                        handle.includes('right')
                                                                        ? 'cursor-nesw-resize'
                                                                        : handle.includes('bottom') &&
                                                                            handle.includes('left')
                                                                            ? 'cursor-nesw-resize'
                                                                            : 'cursor-nwse-resize'
                                                                }
                                                            `}
                                                        />
                                                    ))}

                                                    {[
                                                        'top',
                                                        'right',
                                                        'bottom',
                                                        'left',
                                                    ].map((handle) => (
                                                        <div
                                                            key={handle}
                                                            data-handle={handle}
                                                            onPointerDown={handleCropPointerDown}
                                                            onPointerMove={handleCropPointerMove}
                                                            onPointerUp={handleCropPointerUp}
                                                            onPointerCancel={handleCropPointerUp}
                                                            className={`
                                                                absolute z-20
                                                                rounded-full
                                                                border-2 border-brand-teal
                                                                bg-white
                                                                ${handle === 'top' ||
                                                                    handle === 'bottom'
                                                                    ? 'left-1/2 h-3 w-7 -translate-x-1/2'
                                                                    : 'top-1/2 h-7 w-3 -translate-y-1/2'
                                                                }
                                                                ${handle === 'top'
                                                                    ? '-top-1.5 cursor-ns-resize'
                                                                    : ''
                                                                }
                                                                ${handle === 'bottom'
                                                                    ? '-bottom-1.5 cursor-ns-resize'
                                                                    : ''
                                                                }
                                                                ${handle === 'left'
                                                                    ? '-left-1.5 cursor-ew-resize'
                                                                    : ''
                                                                }
                                                                ${handle === 'right'
                                                                    ? '-right-1.5 cursor-ew-resize'
                                                                    : ''
                                                                }
                                                            `}
                                                        />
                                                    ))}

                                                    <div className="pointer-events-none absolute inset-0 grid grid-cols-3 grid-rows-3">
                                                        {Array.from({ length: 9 }).map((_, index) => (
                                                            <div
                                                                key={index}
                                                                className="border border-white/30"
                                                            />
                                                        ))}
                                                    </div>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                </div>

                                <div
                                    className="
                                        mt-4 flex flex-wrap items-center
                                        justify-between gap-3
                                    "
                                >
                                    <p
                                        className="
                                            text-xs leading-5
                                            text-light-text-muted
                                            dark:text-dark-text-muted
                                        "
                                    >
                                        Drag inside the square to move it.
                                        Drag any edge or corner to resize it.
                                    </p>

                                    <button
                                        type="button"
                                        onClick={handleCropReset}
                                        className="
                                            text-xs font-semibold
                                            text-brand-teal-dark
                                            transition-colors
                                            hover:text-brand-teal
                                            dark:text-brand-teal-light
                                        "
                                    >
                                        Reset selection
                                    </button>
                                </div>

                                {cropError && (
                                    <p
                                        role="alert"
                                        className="
                                            mt-3 rounded-lg
                                            bg-red-50 px-3 py-2
                                            text-sm text-red-700
                                            dark:bg-red-500/10
                                            dark:text-red-300
                                        "
                                    >
                                        {cropError}
                                    </p>
                                )}

                                <div
                                    className="
                                        mt-5 flex flex-col-reverse gap-3
                                        border-t border-light-border-soft
                                        pt-5
                                        dark:border-dark-border-soft
                                        sm:flex-row sm:justify-end
                                    "
                                >
                                    <button
                                        type="button"
                                        onClick={closeCropper}
                                        disabled={isCropping}
                                        className="
                                            rounded-xl
                                            border border-light-border
                                            px-5 py-2.5
                                            text-sm font-semibold
                                            text-light-text-muted
                                            transition-colors
                                            hover:bg-light-surface-soft
                                            disabled:opacity-50
                                            dark:border-dark-border
                                            dark:text-dark-text-muted
                                            dark:hover:bg-dark-surface-soft
                                        "
                                    >
                                        Cancel
                                    </button>

                                    <button
                                        type="button"
                                        onClick={handleConfirmCrop}
                                        disabled={
                                            isCropping ||
                                            !crop ||
                                            !cropImageDimensions.width
                                        }
                                        className="
                                            inline-flex items-center
                                            justify-center gap-2
                                            rounded-xl
                                            bg-brand-teal
                                            px-5 py-2.5
                                            text-sm font-bold text-white
                                            transition-colors
                                            hover:bg-brand-teal-dark
                                            disabled:cursor-not-allowed
                                            disabled:opacity-50
                                        "
                                    >
                                        {isCropping ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Preparing picture...
                                            </>
                                        ) : (
                                            <>
                                                <Check className="h-4 w-4" />
                                                Use this picture
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </ProtectedRoute>
    );
}
