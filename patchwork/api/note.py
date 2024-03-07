# Patchwork - automated patch tracking system
# Copyright (C) 2024 Meta Platforms, Inc. and affiliates.
#
# SPDX-License-Identifier: GPL-2.0-or-later


from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import ListAPIView
from patchwork.api.patch import PatchSerializer
from patchwork.api.user import UserDetailSerializer
from patchwork.api.base import BaseHyperlinkedModelSerializer
from patchwork.models import Note
from patchwork.models import Patch


class NoteSerializer(BaseHyperlinkedModelSerializer):
    submitter = UserDetailSerializer(read_only=True)
    patch = PatchSerializer(read_only=True)

    class Meta:
        model = Note
        fields = [
            'id',
            'patch',
            'submitter',
            'content',
            'created_at',
            'updated_at',
            'maintainer_only',
        ]
        read_only_fields = [
            'id',
            'patch',
            'submitter',
            'created_at',
            'updated_at',
            'maintainer_only',
        ]


class NoteDetailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            patch = Patch.objects.get(id=view.kwargs['patch_id'])
            return (
                patch.project in request.user.profile.maintainer_projects.all()
            )

        note = Note.objects.get(id=view.kwargs['note_id'])
        return (
            note.patch.project
            in request.user.profile.maintainer_projects.all()
        )

    def has_object_permission(self, request, view, obj):
        if (
            not obj.maintainer_only
            and request.method in permissions.SAFE_METHODS
        ):
            return True

        if request.method == 'POST':
            patch = Patch.objects.get(id=view.kwargs['patch_id'])
            return (
                patch.project in request.user.profile.maintainer_projects.all()
            )

        note = Note.objects.get(id=view.kwargs['note_id'])
        return (
            note.patch.project
            in request.user.profile.maintainer_projects.all()
        )


class NoteListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        patch = Patch.objects.get(id=view.kwargs['patch_id'])
        return patch.project in request.user.profile.maintainer_projects.all()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True


class NoteMixin(object):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    lookup_field = 'patch_id'

    def get_queryset(self):
        patch_id = self.kwargs['patch_id']
        get_object_or_404(Patch, id=patch_id)

        return Note.objects.filter(patch=patch_id)


class NoteDetail(NoteMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [NoteDetailPermission]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        note_id = self.kwargs.get('note_id')
        instance = get_object_or_404(queryset, id=note_id)
        self.check_object_permissions(self.request, instance)
        return instance


class NoteList(NoteMixin, CreateAPIView, ListAPIView):
    ordering = 'id'
    permission_classes = [NoteListPermission]

    def get_queryset(self):
        patch_queryset = Patch.objects.all()

        queryset = super().get_queryset()
        public_notes = queryset.filter(maintainer_only=False)
        user_patches = patch_queryset.filter(
            project__in=list(
                self.request.user.profile.maintainer_projects.all()
            )
        )
        maintainer_notes = queryset.filter(
            maintainer_only=True, patch__in=list(user_patches)
        )

        return public_notes | maintainer_notes

    def perform_create(self, serializer):
        serializer.save(
            submitter=self.request.user,
            patch=Patch.objects.get(id=self.kwargs['patch_id']),
        )
        return super().perform_create(serializer)